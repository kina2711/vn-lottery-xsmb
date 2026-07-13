from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Annotated

import typer

from vn_lottery_xsmb.analytics.metrics import write_metric_outputs
from vn_lottery_xsmb.collector.cache import FileCache
from vn_lottery_xsmb.collector.client import SourceClient
from vn_lottery_xsmb.collector.scheduler import resolve_collection_dates
from vn_lottery_xsmb.config.logging import configure_logging
from vn_lottery_xsmb.config.settings import AppSettings, load_settings
from vn_lottery_xsmb.parser.html_parser import LotteryHtmlParser
from vn_lottery_xsmb.parser.normalizer import normalize_draw
from vn_lottery_xsmb.storage.csv_store import CsvStore
from vn_lottery_xsmb.storage.models import SourceRecord
from vn_lottery_xsmb.storage.repository import LotteryRepository
from vn_lottery_xsmb.visualization.charts import create_static_charts
from vn_lottery_xsmb.visualization.dashboard import build_dashboard, build_markdown_report

app = typer.Typer(help="Collect, analyze, and publish Northern Vietnam lottery data.")


def _bootstrap() -> AppSettings:
    settings = load_settings()
    configure_logging(settings.log_level)
    return settings


@app.command()
def collect(
    date_value: Annotated[str | None, typer.Option("--date")] = None,
    start_date: Annotated[str | None, typer.Option("--start-date")] = None,
    end_date: Annotated[str | None, typer.Option("--end-date")] = None,
    source: Annotated[str | None, typer.Option("--source")] = None,
    refresh: bool = False,
    dry_run: bool = False,
) -> None:
    settings = _bootstrap()
    dates = resolve_collection_dates(date_value, start_date, end_date)
    source_name = source or settings.source_name
    client = SourceClient(
        settings.base_url,
        FileCache(settings.cache_dir),
        settings.request_timeout_seconds,
        settings.retry_attempts,
    )
    parser = LotteryHtmlParser()
    store = CsvStore(settings.draws_csv, settings.prizes_csv)
    repository = LotteryRepository(store)
    draws = []
    for draw_date in dates:
        fetched = client.fetch(draw_date, refresh=refresh)
        raw_draw = parser.parse(fetched.content)
        draws.append(
            normalize_draw(
                raw_draw,
                SourceRecord(
                    source_name=source_name,
                    source_url=fetched.url,
                    http_status=fetched.status_code,
                    cache_key=fetched.cache_key,
                ),
            )
        )
    if dry_run:
        typer.echo(f"validated {len(draws)} draw(s); dry-run skipped storage writes")
        return
    summary = repository.save_draws(draws)
    typer.echo(
        f"collect completed added={summary.added} updated={summary.updated} "
        f"unchanged={summary.unchanged} rejected={summary.rejected} failed={summary.failed} "
        f"storage={settings.processed_dir}"
    )
    if summary.failed:
        raise typer.Exit(code=1)


@app.command()
def update(
    from_date: Annotated[str | None, typer.Option("--from")] = None,
    to_date: Annotated[str | None, typer.Option("--to")] = None,
    refresh: bool = False,
    dry_run: bool = False,
) -> None:
    settings = _bootstrap()
    store = CsvStore(settings.draws_csv, settings.prizes_csv)
    latest = store.latest_draw_date()
    if from_date is None:
        if latest is None:
            raise typer.BadParameter("provide --from when storage is empty")
        from_date = latest.isoformat()
    if to_date is None:
        to_date = from_date
    collect(None, from_date, to_date, None, refresh, dry_run)


@app.command()
def analyze(
    start_date: Annotated[str | None, typer.Option("--start-date")] = None,
    end_date: Annotated[str | None, typer.Option("--end-date")] = None,
    window: Annotated[int | None, typer.Option("--window")] = None,
    output_dir: Annotated[Path | None, typer.Option("--output-dir")] = None,
) -> None:
    settings = _bootstrap()
    store = CsvStore(settings.draws_csv, settings.prizes_csv)
    prizes = store.load_prizes()
    if prizes.empty:
        typer.echo("no prize data available for analysis")
        raise typer.Exit(code=1)
    if start_date:
        prizes = prizes.loc[prizes["draw_date"] >= start_date]
    if end_date:
        prizes = prizes.loc[prizes["draw_date"] <= end_date]
    outputs = write_metric_outputs(prizes, output_dir or settings.report_dir, window or settings.rolling_window_days)
    typer.echo(f"analyze completed files={len(outputs)} output={output_dir or settings.report_dir}")


@app.command()
def report(
    output: Annotated[Path | None, typer.Option("--output")] = None,
    title: Annotated[str | None, typer.Option("--title")] = None,
) -> None:
    settings = _bootstrap()
    report_path = output or (settings.docs_dir / "report.md")
    build_markdown_report(settings.report_dir, report_path, title or "Báo cáo XSMB")
    typer.echo(f"report completed output={report_path}")


@app.command()
def visualize(
    output_dir: Annotated[Path | None, typer.Option("--output-dir")] = None,
    theme: Annotated[str, typer.Option("--theme")] = "light",
) -> None:
    settings = _bootstrap()
    docs_dir = output_dir or settings.docs_dir
    charts = create_static_charts(settings.report_dir, docs_dir / "assets")
    dashboard_path = build_dashboard(settings.report_dir, docs_dir / "index.html")
    typer.echo(f"visualize completed dashboard={dashboard_path} charts={len(charts)} theme={theme}")


@app.command("run-daily")
def run_daily(
    refresh: bool = False,
    fail_on_no_data: Annotated[bool, typer.Option("--fail-on-no-data")] = False,
) -> None:
    settings = _bootstrap()
    store = CsvStore(settings.draws_csv, settings.prizes_csv)
    today = date.today().isoformat()
    try:
        collect(today, None, None, None, refresh, False)
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"daily collection skipped or failed for {today}: {exc}")
    prizes = store.load_prizes()
    if prizes.empty:
        typer.echo("no prize data available; daily pipeline skipped downstream artifacts")
        if fail_on_no_data:
            raise typer.Exit(code=1)
        return
    outputs = write_metric_outputs(prizes, settings.report_dir, settings.rolling_window_days)
    report_path = build_markdown_report(settings.report_dir, settings.docs_dir / "report.md")
    charts = create_static_charts(settings.report_dir, settings.docs_dir / "assets")
    dashboard_path = build_dashboard(settings.report_dir, settings.docs_dir / "index.html")
    visible_changes = [str(path) for path in [*outputs.values(), *charts.values(), report_path, dashboard_path]]
    typer.echo(
        "run-daily completed "
        f"refresh={refresh} artifacts={len(visible_changes)} changed_files="
        + ",".join(visible_changes)
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
