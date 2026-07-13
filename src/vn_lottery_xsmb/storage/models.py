from __future__ import annotations

from datetime import UTC, date, datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator


class ValidationStatus(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WARNING = "warning"


class RunStatus(StrEnum):
    SUCCEEDED = "succeeded"
    PARTIAL = "partial"
    FAILED = "failed"
    NO_CHANGE = "no_change"


class SourceRecord(BaseModel):
    source_name: str = Field(min_length=1)
    source_url: str | HttpUrl
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    http_status: int | None = None
    cache_key: str | None = None

    @field_validator("http_status")
    @classmethod
    def http_status_must_be_valid(cls, value: int | None) -> int | None:
        if value is not None and not 100 <= value <= 599:
            raise ValueError("http_status must be between 100 and 599")
        return value


class PrizeEntry(BaseModel):
    draw_date: date
    prize_group: str = Field(min_length=1)
    position: int = Field(ge=1)
    raw_value: str = Field(min_length=1)
    normalized_value: str = Field(min_length=1)
    last_two_digits: str = Field(pattern=r"^\d{2}$")

    @field_validator("normalized_value")
    @classmethod
    def normalized_value_must_be_numeric(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("normalized_value must contain only digits")
        return value


class DrawResult(BaseModel):
    draw_date: date
    region: str = "mien-bac"
    prizes: list[PrizeEntry]
    source: SourceRecord
    collected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    validation_status: ValidationStatus = ValidationStatus.ACCEPTED
    validation_messages: list[str] = Field(default_factory=list)
    content_hash: str = Field(min_length=1)

    @model_validator(mode="after")
    def ensure_prizes_match_draw_date(self) -> DrawResult:
        if not self.prizes:
            raise ValueError("draw result must include at least one prize")
        for prize in self.prizes:
            if prize.draw_date != self.draw_date:
                raise ValueError("all prize entries must match draw_date")
        return self


class CollectionRun(BaseModel):
    run_id: str = Field(min_length=1)
    started_at: datetime
    finished_at: datetime | None = None
    requested_start_date: date
    requested_end_date: date
    source_name: str = Field(min_length=1)
    records_seen: int = Field(default=0, ge=0)
    records_added: int = Field(default=0, ge=0)
    records_updated: int = Field(default=0, ge=0)
    records_rejected: int = Field(default=0, ge=0)
    records_unchanged: int = Field(default=0, ge=0)
    status: RunStatus = RunStatus.SUCCEEDED
    error_message: str | None = None

    @model_validator(mode="after")
    def validate_run_times_and_errors(self) -> CollectionRun:
        if self.finished_at and self.finished_at < self.started_at:
            raise ValueError("finished_at must not be earlier than started_at")
        if self.status == RunStatus.FAILED and not self.error_message:
            raise ValueError("failed runs must include an error_message")
        return self


class AnalysisSnapshot(BaseModel):
    snapshot_id: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    dataset_start_date: date
    dataset_end_date: date
    record_count: int = Field(ge=0)
    metrics: dict[str, Path] = Field(default_factory=dict)
    parameters: dict[str, str | int | float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_date_range(self) -> AnalysisSnapshot:
        if self.dataset_start_date > self.dataset_end_date:
            raise ValueError("dataset_start_date must not be after dataset_end_date")
        return self


class ReportArtifact(BaseModel):
    path: Path
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    dataset_start_date: date | None = None
    dataset_end_date: date | None = None
    sections: list[str] = Field(default_factory=list)
    asset_links: list[str] = Field(default_factory=list)


class DashboardArtifact(BaseModel):
    path: Path
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    chart_ids: list[str] = Field(default_factory=list)
    dataset_start_date: date | None = None
    dataset_end_date: date | None = None
