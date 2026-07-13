from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CacheEntry:
    key: str
    path: Path
    exists: bool


class FileCache:
    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir

    def key_for(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def path_for(self, key: str) -> Path:
        return self.cache_dir / f"{key}.html"

    def get(self, key: str) -> str | None:
        path = self.path_for(key)
        return path.read_text(encoding="utf-8") if path.exists() else None

    def set(self, key: str, content: str) -> Path:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        path = self.path_for(key)
        path.write_text(content, encoding="utf-8")
        return path

    def entry_for(self, value: str) -> CacheEntry:
        key = self.key_for(value)
        path = self.path_for(key)
        return CacheEntry(key, path, path.exists())
