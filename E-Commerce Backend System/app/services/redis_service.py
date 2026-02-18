"""
Redis cache-aside pattern + sliding window rate limiter.
Graceful degradation when Redis is unavailable.
"""

import json
import time
import redis
import structlog

from app.config import settings

logger = structlog.get_logger()


class RedisService:
    def __init__(self):
        self._client: redis.Redis | None = None
        self._available = False

    def connect(self) -> bool:
        if not settings.redis_enabled:
            return False
        try:
            self._client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_timeout=2,
                socket_connect_timeout=2,
            )
            self._client.ping()
            self._available = True
            logger.info("redis_connected")
            return True
        except Exception as e:
            logger.warning("redis_unavailable", error=str(e))
            self._available = False
            return False

    @property
    def is_available(self) -> bool:
        return self._available

    # --- Cache-aside ---
    def cache_get(self, key: str) -> dict | list | None:
        if not self._available:
            return None
        try:
            raw = self._client.get(f"ecom:{key}")
            return json.loads(raw) if raw else None
        except Exception:
            return None

    def cache_set(self, key: str, data, ttl: int = None) -> None:
        if not self._available:
            return
        try:
            self._client.setex(
                f"ecom:{key}",
                ttl or settings.redis_cache_ttl,
                json.dumps(data, default=str),
            )
        except Exception:
            pass

    def cache_delete(self, key: str) -> None:
        if not self._available:
            return
        try:
            self._client.delete(f"ecom:{key}")
        except Exception:
            pass

    def cache_invalidate_pattern(self, pattern: str) -> int:
        if not self._available:
            return 0
        try:
            keys = self._client.keys(f"ecom:{pattern}")
            if keys:
                return self._client.delete(*keys)
            return 0
        except Exception:
            return 0

    # --- Rate Limiting (sliding window) ---
    def check_rate_limit(self, client_ip: str) -> tuple[bool, int]:
        """
        Returns (allowed: bool, remaining: int).
        Uses Redis sorted set sliding window.
        """
        if not self._available:
            return True, settings.redis_rate_limit_max

        key = f"ecom:rate:{client_ip}"
        now = time.time()
        window_start = now - settings.redis_rate_limit_window

        try:
            pipe = self._client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, settings.redis_rate_limit_window + 1)
            results = pipe.execute()

            count = results[2]
            remaining = max(0, settings.redis_rate_limit_max - count)
            allowed = count <= settings.redis_rate_limit_max

            return allowed, remaining
        except Exception:
            return True, settings.redis_rate_limit_max

    def get_stats(self) -> dict:
        if not self._available:
            return {"available": False}
        try:
            info = self._client.info("stats")
            return {
                "available": True,
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
            }
        except Exception:
            return {"available": False}

    def disconnect(self):
        if self._client:
            self._client.close()
            self._available = False


redis_service = RedisService()
