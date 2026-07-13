from pathlib import Path


def test_daily_workflow_contains_schedule_and_pages_publish() -> None:
    workflow = Path(".github/workflows/daily-update.yml").read_text(encoding="utf-8")

    assert "cron:" in workflow
    assert "vn-lottery run-daily" in workflow
    assert "actions/deploy-pages" in workflow
