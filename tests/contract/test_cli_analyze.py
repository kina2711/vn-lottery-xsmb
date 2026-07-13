from typer.testing import CliRunner

from vn_lottery_xsmb.cli.app import app


def test_analyze_command_accepts_options(monkeypatch) -> None:
    data_dir = ".test-output/cli-analyze-data"
    processed = __import__("pathlib").Path(data_dir) / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    prizes = __import__("pathlib").Path("tests/fixtures/prizes_sample.csv").read_text(encoding="utf-8")
    (processed / "prizes.csv").write_text(prizes, encoding="utf-8")
    monkeypatch.setenv("VN_LOTTERY_DATA_DIR", data_dir)
    monkeypatch.setenv("VN_LOTTERY_REPORT_DIR", ".test-output/cli-reports")

    result = CliRunner().invoke(
        app,
        [
            "analyze",
            "--start-date",
            "2026-07-10",
            "--end-date",
            "2026-07-12",
            "--window",
            "2",
            "--output-dir",
            ".test-output/cli-reports",
        ],
    )

    assert result.exit_code == 0
