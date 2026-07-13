from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from vn_lottery_xsmb.storage.models import DrawResult


class StorageAction(StrEnum):
    ADDED = "added"
    UPDATED = "updated"
    UNCHANGED = "unchanged"
    REJECTED = "rejected"
    FAILED = "failed"


@dataclass(frozen=True)
class StorageError:
    message: str
    detail: str | None = None


@dataclass
class UpdateSummary:
    added: int = 0
    updated: int = 0
    unchanged: int = 0
    rejected: int = 0
    failed: int = 0
    messages: list[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return self.added > 0 or self.updated > 0

    def record(self, action: StorageAction, message: str | None = None) -> None:
        if action == StorageAction.ADDED:
            self.added += 1
        elif action == StorageAction.UPDATED:
            self.updated += 1
        elif action == StorageAction.UNCHANGED:
            self.unchanged += 1
        elif action == StorageAction.REJECTED:
            self.rejected += 1
        elif action == StorageAction.FAILED:
            self.failed += 1
        if message:
            self.messages.append(message)


class LotteryRepository:
    def __init__(self, store: object) -> None:
        self.store = store

    def save_draws(self, draws: list[DrawResult]) -> UpdateSummary:
        summary = UpdateSummary()
        for draw in draws:
            try:
                result = self.store.upsert(draw)  # type: ignore[attr-defined]
                summary.record(result.action, f"{result.draw_date.isoformat()}: {result.action.value}")
            except Exception as exc:  # noqa: BLE001
                summary.record(StorageAction.FAILED, f"{draw.draw_date.isoformat()}: {exc}")
        return summary
