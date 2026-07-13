from pathlib import Path

from typer.testing import CliRunner

from vn_lottery_xsmb.cli.app import app


def test_run_daily_generates_artifacts(monkeypatch) -> None:
    data_dir = Path(".test-output/run-daily-data")
    processed = data_dir / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    processed.joinpath("prizes.csv").write_text(
        Path("tests/fixtures/prizes_sample.csv").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    monkeypatch.setenv("VN_LOTTERY_DATA_DIR", str(data_dir))
    monkeypatch.setenv("VN_LOTTERY_REPORT_DIR", ".test-output/run-daily-reports")
    monkeypatch.setenv("VN_LOTTERY_DOCS_DIR", ".test-output/run-daily-docs")

    result = CliRunner().invoke(app, ["run-daily"])

    assert result.exit_code == 0
    assert Path(".test-output/run-daily-docs/index.html").exists()
    assert Path(".test-output/run-daily-docs/report.md").exists()
