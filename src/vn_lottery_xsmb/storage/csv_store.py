from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd

from vn_lottery_xsmb.storage.models import DrawResult, PrizeEntry
from vn_lottery_xsmb.storage.repository import StorageAction

DRAW_FIELDS = [
    "draw_date",
    "region",
    "source_name",
    "source_url",
    "collected_at",
    "validation_status",
    "validation_messages",
    "content_hash",
]
PRIZE_FIELDS = [
    "draw_date",
    "prize_group",
    "position",
    "raw_value",
    "normalized_value",
    "last_two_digits",
]


@dataclass(frozen=True)
class StoreWriteResult:
    action: StorageAction
    draw_date: date


class CsvStore:
    def __init__(self, draws_path: Path, prizes_path: Path) -> None:
        self.draws_path = draws_path
        self.prizes_path = prizes_path

    def ensure_parent_dirs(self) -> None:
        self.draws_path.parent.mkdir(parents=True, exist_ok=True)
        self.prizes_path.parent.mkdir(parents=True, exist_ok=True)

    def load_draws(self) -> pd.DataFrame:
        if not self.draws_path.exists():
            return pd.DataFrame(columns=DRAW_FIELDS)
        return pd.read_csv(self.draws_path, dtype=str)

    def load_prizes(self) -> pd.DataFrame:
        if not self.prizes_path.exists():
            return pd.DataFrame(columns=PRIZE_FIELDS)
        return pd.read_csv(self.prizes_path, dtype=str)

    def existing_hash(self, draw_date: date) -> str | None:
        draws = self.load_draws()
        if draws.empty:
            return None
        matches = draws.loc[draws["draw_date"] == draw_date.isoformat()]
        if matches.empty:
            return None
        return str(matches.iloc[0]["content_hash"])

    def upsert(self, draw: DrawResult) -> StoreWriteResult:
        self.ensure_parent_dirs()
        existing_hash = self.existing_hash(draw.draw_date)
        if existing_hash == draw.content_hash:
            return StoreWriteResult(StorageAction.UNCHANGED, draw.draw_date)

        draws = self.load_draws()
        prizes = self.load_prizes()
        date_key = draw.draw_date.isoformat()
        if not draws.empty:
            draws = draws.loc[draws["draw_date"] != date_key]
        if not prizes.empty:
            prizes = prizes.loc[prizes["draw_date"] != date_key]

        draw_row = pd.DataFrame([self._draw_row(draw)], columns=DRAW_FIELDS)
        prize_rows = pd.DataFrame([self._prize_row(prize) for prize in draw.prizes], columns=PRIZE_FIELDS)
        draws = pd.concat([draws, draw_row], ignore_index=True).sort_values("draw_date")
        prizes = pd.concat([prizes, prize_rows], ignore_index=True).sort_values(
            ["draw_date", "prize_group", "position"]
        )
        self._write_dataframe(draws, self.draws_path, DRAW_FIELDS)
        self._write_dataframe(prizes, self.prizes_path, PRIZE_FIELDS)
        return StoreWriteResult(
            StorageAction.ADDED if existing_hash is None else StorageAction.UPDATED,
            draw.draw_date,
        )

    def latest_draw_date(self) -> date | None:
        draws = self.load_draws()
        if draws.empty:
            return None
        return date.fromisoformat(str(draws["draw_date"].max()))

    def _draw_row(self, draw: DrawResult) -> dict[str, str]:
        return {
            "draw_date": draw.draw_date.isoformat(),
            "region": draw.region,
            "source_name": draw.source.source_name,
            "source_url": str(draw.source.source_url),
            "collected_at": draw.collected_at.isoformat(),
            "validation_status": draw.validation_status.value,
            "validation_messages": "; ".join(draw.validation_messages),
            "content_hash": draw.content_hash,
        }

    def _prize_row(self, prize: PrizeEntry) -> dict[str, str]:
        return {
            "draw_date": prize.draw_date.isoformat(),
            "prize_group": prize.prize_group,
            "position": str(prize.position),
            "raw_value": prize.raw_value,
            "normalized_value": prize.normalized_value,
            "last_two_digits": prize.last_two_digits,
        }

    def _write_dataframe(self, frame: pd.DataFrame, path: Path, fields: list[str]) -> None:
        temp_path = path.with_suffix(path.suffix + ".tmp")
        frame.to_csv(temp_path, index=False, columns=fields, quoting=csv.QUOTE_MINIMAL)
        try:
            temp_path.replace(path)
        except PermissionError:
            frame.to_csv(path, index=False, columns=fields, quoting=csv.QUOTE_MINIMAL)
