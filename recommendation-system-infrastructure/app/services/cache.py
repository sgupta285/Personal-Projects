from __future__ import annotations

import json
import time
from dataclasses import dataclass

from app.services.metrics import CACHE_HITS


@dataclass
class CacheEntry:
    value: dict
    expires_at: float


class TTLCache:
    def __init__(self, ttl_seconds: int = 120) -> None:
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, CacheEntry] = {}

    def get(self, key: str) -> dict | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.time() > entry.expires_at:
            self._store.pop(key, None)
            return None
        CACHE_HITS.inc()
        return entry.value

    def set(self, key: str, value: dict) -> None:
        self._store[key] = CacheEntry(value=value, expires_at=time.time() + self.ttl_seconds)

    @staticmethod
    def build_key(payload: dict) -> str:
        return json.dumps(payload, sort_keys=True)
