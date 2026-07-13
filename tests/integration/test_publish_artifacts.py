from pathlib import Path

from vn_lottery_xsmb.visualization.charts import create_static_charts
from vn_lottery_xsmb.visualization.dashboard import build_dashboard, build_markdown_report


def test_publish_artifacts() -> None:
    docs = Path(".test-output/docs")
    assets = docs / "assets"

    create_static_charts(Path("tests/fixtures/metrics_sample"), assets)
    report = build_markdown_report(Path("tests/fixtures/metrics_sample"), docs / "report.md")
    dashboard = build_dashboard(Path("tests/fixtures/metrics_sample"), docs / "index.html")

    assert report.exists()
    assert dashboard.exists()
    assert (assets / "frequency.png").exists()
