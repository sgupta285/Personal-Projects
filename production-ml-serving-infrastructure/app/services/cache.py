import json
from typing import Any

from cachetools import TTLCache

from app.core.config import settings
from app.services.metrics import CACHE_COUNTER

try:
    import redis.asyncio as redis
except Exception:
    redis = None


class PredictionCache:
    def __init__(self) -> None:
        self.local_cache: TTLCache[str, Any] = TTLCache(
            maxsize=settings.in_memory_cache_maxsize,
            ttl=settings.in_memory_cache_ttl_seconds,
        )
        self.redis_client = None
        if settings.enable_redis and redis is not None:
            self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)

    async def get(self, key: str) -> Any | None:
        if key in self.local_cache:
            CACHE_COUNTER.labels(layer="memory", result="hit").inc()
            return self.local_cache[key]
        CACHE_COUNTER.labels(layer="memory", result="miss").inc()
        if not self.redis_client:
            return None
        value = await self.redis_client.get(key)
        if value is None:
            CACHE_COUNTER.labels(layer="redis", result="miss").inc()
            return None
        CACHE_COUNTER.labels(layer="redis", result="hit").inc()
        parsed = json.loads(value)
        self.local_cache[key] = parsed
        return parsed

    async def set(self, key: str, value: Any) -> None:
        self.local_cache[key] = value
        if self.redis_client:
            await self.redis_client.setex(
                key,
                settings.redis_cache_ttl_seconds,
                json.dumps(value),
            )

    async def clear(self) -> None:
        self.local_cache.clear()
        if self.redis_client:
            await self.redis_client.flushdb()

    async def close(self) -> None:
        if self.redis_client:
            await self.redis_client.close()
