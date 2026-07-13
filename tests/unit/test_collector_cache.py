from pathlib import Path

from vn_lottery_xsmb.collector.cache import FileCache


def test_file_cache_roundtrip() -> None:
    cache = FileCache(Path(".test-output/cache"))
    key = cache.key_for("https://example.test/2026-07-13")

    path = cache.set(key, "<html>ok</html>")

    assert path.exists()
    assert cache.get(key) == "<html>ok</html>"
    assert cache.entry_for("https://example.test/2026-07-13").exists
