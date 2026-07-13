from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from time import sleep

import httpx

from vn_lottery_xsmb.collector.cache import FileCache

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class FetchResult:
    url: str
    content: str
    status_code: int
    cache_key: str
    from_cache: bool


class SourceClient:
    def __init__(
        self,
        base_url: str,
        cache: FileCache,
        timeout_seconds: int,
        retry_attempts: int,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url
        self.cache = cache
        self.timeout_seconds = timeout_seconds
        self.retry_attempts = retry_attempts
        self.client = client or httpx.Client(timeout=timeout_seconds)

    def url_for(self, draw_date: date) -> str:
        return self.base_url.format(
            date=draw_date.isoformat(),
            date_dmy=draw_date.strftime("%d-%m-%Y"),
        )

    def fetch(self, draw_date: date, refresh: bool = False) -> FetchResult:
        url = self.url_for(draw_date)
        cache_key = self.cache.key_for(url)
        if not refresh:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return FetchResult(url, cached, 200, cache_key, True)

        last_error: Exception | None = None
        for attempt in range(1, self.retry_attempts + 1):
            try:
                response = self.client.get(url, timeout=self.timeout_seconds)
                response.raise_for_status()
                self.cache.set(cache_key, response.text)
                return FetchResult(url, response.text, response.status_code, cache_key, False)
            except (httpx.HTTPError, httpx.TimeoutException) as exc:
                last_error = exc
                LOGGER.warning("Fetch attempt %s failed for %s: %s", attempt, url, exc)
                if attempt < self.retry_attempts:
                    sleep(min(attempt, 3) * 0.1)
        raise RuntimeError(f"Failed to fetch {url} after {self.retry_attempts} attempts") from last_error
