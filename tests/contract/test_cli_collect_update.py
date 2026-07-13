from typer.testing import CliRunner

from vn_lottery_xsmb.cli.app import app


def test_collect_requires_date_or_range() -> None:
    result = CliRunner().invoke(app, ["collect", "--dry-run"])

    assert result.exit_code != 0


def test_update_requires_from_when_storage_empty(monkeypatch) -> None:
    monkeypatch.setenv("VN_LOTTERY_DATA_DIR", ".test-output/empty-data")
    monkeypatch.setenv("VN_LOTTERY_CACHE_DIR", ".test-output/empty-cache")
    result = CliRunner().invoke(app, ["update", "--dry-run"])

    assert result.exit_code != 0
