from pathlib import Path

from vn_lottery_xsmb.visualization.dashboard import build_markdown_report


def test_build_markdown_report() -> None:
    output = build_markdown_report(
        Path("tests/fixtures/metrics_sample"),
        Path(".test-output/report/report.md"),
        title="Test Report",
    )

    content = output.read_text(encoding="utf-8")
    assert "# Test Report" in content
    assert "Top Frequency" in content
