from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass


@dataclass(slots=True)
class CacheStats:
    hits: int = 0
    misses: int = 0
    evictions: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0.0


class MemoryCache:
    def __init__(self, capacity_bytes: int = 64 * 1024 * 1024) -> None:
        self.capacity_bytes = capacity_bytes
        self.current_bytes = 0
        self.store: OrderedDict[str, bytes] = OrderedDict()
        self.stats = CacheStats()

    def get(self, key: str) -> bytes | None:
        value = self.store.get(key)
        if value is None:
            self.stats.misses += 1
            return None
        self.store.move_to_end(key)
        self.stats.hits += 1
        return value

    def set(self, key: str, value: bytes) -> None:
        if key in self.store:
            old = self.store.pop(key)
            self.current_bytes -= len(old)

        while self.current_bytes + len(value) > self.capacity_bytes and self.store:
            _, evicted = self.store.popitem(last=False)
            self.current_bytes -= len(evicted)
            self.stats.evictions += 1

        if len(value) > self.capacity_bytes:
            return

        self.store[key] = value
        self.current_bytes += len(value)

    def reset_stats(self) -> None:
        self.stats = CacheStats()

    def clear(self) -> None:
        self.store.clear()
        self.current_bytes = 0
        self.reset_stats()
