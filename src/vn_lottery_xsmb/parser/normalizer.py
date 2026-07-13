from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from vn_lottery_xsmb.parser.html_parser import RawDraw
from vn_lottery_xsmb.storage.models import DrawResult, PrizeEntry, SourceRecord


def normalize_digits(value: str) -> str:
    digits = "".join(character for character in value if character.isdigit())
    if not digits:
        raise ValueError("prize value does not contain digits")
    return digits


def content_hash(prizes: list[PrizeEntry]) -> str:
    payload = "|".join(
        f"{item.prize_group}:{item.position}:{item.normalized_value}" for item in prizes
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalize_draw(raw_draw: RawDraw, source: SourceRecord) -> DrawResult:
    entries: list[PrizeEntry] = []
    for raw_prize in raw_draw.prizes:
        for position, raw_value in enumerate(raw_prize.values, start=1):
            normalized = normalize_digits(raw_value)
            entries.append(
                PrizeEntry(
                    draw_date=raw_draw.draw_date,
                    prize_group=raw_prize.prize_group,
                    position=position,
                    raw_value=raw_value,
                    normalized_value=normalized,
                    last_two_digits=normalized[-2:].zfill(2),
                )
            )
    return DrawResult(
        draw_date=raw_draw.draw_date,
        region=raw_draw.region,
        prizes=entries,
        source=source,
        collected_at=datetime.now(UTC),
        content_hash=content_hash(entries),
    )
