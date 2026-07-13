from typer.testing import CliRunner

from vn_lottery_xsmb.cli.app import app


def test_report_command_accepts_options(monkeypatch) -> None:
    monkeypatch.setenv("VN_LOTTERY_REPORT_DIR", "tests/fixtures/metrics_sample")
    result = CliRunner().invoke(app, ["report", "--output", ".test-output/cli-report.md"])

    assert result.exit_code == 0


def test_visualize_command_accepts_options(monkeypatch) -> None:
    monkeypatch.setenv("VN_LOTTERY_REPORT_DIR", "tests/fixtures/metrics_sample")
    result = CliRunner().invoke(app, ["visualize", "--output-dir", ".test-output/cli-docs"])

    assert result.exit_code == 0
