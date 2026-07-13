from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from vn_lottery_xsmb.storage.models import (
    CollectionRun,
    DrawResult,
    PrizeEntry,
    RunStatus,
    SourceRecord,
)


def test_prize_entry_requires_numeric_value() -> None:
    with pytest.raises(ValidationError):
        PrizeEntry(
            draw_date=date(2026, 7, 13),
            prize_group="special",
            position=1,
            raw_value="12A45",
            normalized_value="12A45",
            last_two_digits="45",
        )


def test_draw_result_requires_matching_prize_dates() -> None:
    prize = PrizeEntry(
        draw_date=date(2026, 7, 12),
        prize_group="special",
        position=1,
        raw_value="12345",
        normalized_value="12345",
        last_two_digits="45",
    )

    with pytest.raises(ValidationError):
        DrawResult(
            draw_date=date(2026, 7, 13),
            prizes=[prize],
            source=SourceRecord(source_name="fixture", source_url="https://example.test"),
            content_hash="abc",
        )


def test_failed_collection_run_requires_error_message() -> None:
    with pytest.raises(ValidationError):
        CollectionRun(
            run_id="run-1",
            started_at=datetime(2026, 7, 13, tzinfo=UTC),
            requested_start_date=date(2026, 7, 13),
            requested_end_date=date(2026, 7, 13),
            source_name="fixture",
            status=RunStatus.FAILED,
        )
