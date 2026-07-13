from pathlib import Path

import pytest
from pydantic import ValidationError

from vn_lottery_xsmb.config.settings import AppSettings


def test_settings_accept_valid_base_url() -> None:
    data_dir = Path("data")
    settings = AppSettings(base_url="https://example.test/{date}", data_dir=data_dir)

    assert settings.base_url == "https://example.test/{date}"
    assert settings.processed_dir == data_dir / "processed"


def test_settings_reject_base_url_without_date_placeholder() -> None:
    with pytest.raises(ValidationError):
        AppSettings(base_url="https://example.test/latest")
