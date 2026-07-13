from typer.testing import CliRunner

from vn_lottery_xsmb.cli.app import app


def test_cli_lists_expected_commands() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    for command in ["collect", "update", "analyze", "report", "visualize", "run-daily"]:
        assert command in result.output
