from typer.testing import CliRunner

from vn_lottery_xsmb.cli.app import app


def test_analyze_fails_without_data(monkeypatch) -> None:
    monkeypatch.setenv("VN_LOTTERY_DATA_DIR", ".test-output/missing-data")

    result = CliRunner().invoke(app, ["analyze"])

    assert result.exit_code != 0
    assert "no prize data" in result.output
