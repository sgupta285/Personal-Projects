from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any

from app.core.metrics import CACHE_HITS


@dataclass
class CacheEntry:
    expires_at: float
    value: Any


class MemoryCache:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, CacheEntry] = {}

    def make_key(self, namespace: str, payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, sort_keys=True).encode("utf-8")
        digest = hashlib.sha256(raw).hexdigest()
        return f"{namespace}:{digest}"

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if not entry:
            return None
        if entry.expires_at < time.time():
            self._store.pop(key, None)
            return None
        CACHE_HITS.labels(cache_name="memory").inc()
        return entry.value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = CacheEntry(expires_at=time.time() + self.ttl_seconds, value=value)
