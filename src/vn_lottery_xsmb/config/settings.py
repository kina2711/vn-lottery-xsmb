from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import PositiveInt, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="VN_LOTTERY_", extra="ignore")

    source_name: str = "minh-ngoc"
    base_url: str = "https://www.minhngoc.net.vn/ket-qua-xo-so/mien-bac/{date_dmy}.html"
    data_dir: Path = Path("data")
    cache_dir: Path = Path("data/cache")
    report_dir: Path = Path("data/reports")
    docs_dir: Path = Path("docs")
    request_timeout_seconds: PositiveInt = 15
    retry_attempts: PositiveInt = 3
    rolling_window_days: PositiveInt = 30
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    @field_validator("base_url")
    @classmethod
    def base_url_must_support_date(cls, value: str) -> str:
        if "{date}" not in value and "{date_dmy}" not in value:
            raise ValueError("base_url must contain {date} or {date_dmy}")
        return value

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"

    @property
    def draws_csv(self) -> Path:
        return self.processed_dir / "draws.csv"

    @property
    def prizes_csv(self) -> Path:
        return self.processed_dir / "prizes.csv"


def load_settings() -> AppSettings:
    return AppSettings()
