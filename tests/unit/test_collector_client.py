from datetime import date
from pathlib import Path

import httpx

from vn_lottery_xsmb.collector.cache import FileCache
from vn_lottery_xsmb.collector.client import SourceClient


def test_source_client_fetches_and_caches_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<html>fresh</html>", request=request)

    cache = FileCache(Path(".test-output/client-cache"))
    client = SourceClient(
        "https://example.test/{date}",
        cache,
        timeout_seconds=1,
        retry_attempts=1,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    result = client.fetch(date(2026, 7, 13), refresh=True)
    cached = client.fetch(date(2026, 7, 13))

    assert result.content == "<html>fresh</html>"
    assert not result.from_cache
    assert cached.from_cache
