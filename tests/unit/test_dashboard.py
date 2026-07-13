from pathlib import Path

from vn_lottery_xsmb.visualization.dashboard import build_dashboard


def test_build_dashboard_html() -> None:
    output = build_dashboard(
        Path("tests/fixtures/metrics_sample"),
        Path(".test-output/dashboard/index.html"),
    )

    content = output.read_text(encoding="utf-8")
    assert "Northern Lottery Dashboard" in content
    assert "Frequency" in content
