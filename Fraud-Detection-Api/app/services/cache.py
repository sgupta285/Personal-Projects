"""
Redis cache-aside pattern for fraud predictions.
Caches predictions by transaction feature hash to avoid redundant inference.
"""

import hashlib
import json
import redis
import structlog

from app.config import settings

logger = structlog.get_logger()


class CacheService:
    def __init__(self):
        self._client: redis.Redis | None = None
        self._available = False

    def connect(self) -> bool:
        if not settings.redis_enabled:
            logger.info("cache_disabled")
            return False

        try:
            self._client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_timeout=2,
                socket_connect_timeout=2,
                retry_on_timeout=True,
            )
            self._client.ping()
            self._available = True
            logger.info("cache_connected", url=settings.redis_url)
            return True
        except Exception as e:
            logger.warning("cache_connection_failed", error=str(e))
            self._available = False
            return False

    @property
    def is_available(self) -> bool:
        return self._available

    @staticmethod
    def _feature_key(features: list[float]) -> str:
        """Deterministic hash of feature vector for cache keying."""
        raw = json.dumps([round(f, 6) for f in features], sort_keys=True)
        h = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return f"fraud:pred:{h}"

    def get_prediction(self, features: list[float]) -> dict | None:
        if not self._available or not self._client:
            return None
        try:
            key = self._feature_key(features)
            cached = self._client.get(key)
            if cached:
                logger.debug("cache_hit", key=key)
                return json.loads(cached)
            return None
        except Exception as e:
            logger.warning("cache_get_error", error=str(e))
            return None

    def set_prediction(self, features: list[float], result: dict) -> None:
        if not self._available or not self._client:
            return
        try:
            key = self._feature_key(features)
            self._client.setex(key, settings.redis_cache_ttl, json.dumps(result))
            logger.debug("cache_set", key=key, ttl=settings.redis_cache_ttl)
        except Exception as e:
            logger.warning("cache_set_error", error=str(e))

    def get_stats(self) -> dict:
        if not self._available or not self._client:
            return {"available": False}
        try:
            info = self._client.info("stats")
            return {
                "available": True,
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "connected_clients": self._client.info("clients").get("connected_clients", 0),
            }
        except Exception:
            return {"available": False}

    def flush(self) -> int:
        """Flush all fraud prediction caches."""
        if not self._available or not self._client:
            return 0
        try:
            keys = self._client.keys("fraud:pred:*")
            if keys:
                return self._client.delete(*keys)
            return 0
        except Exception:
            return 0

    def disconnect(self):
        if self._client:
            self._client.close()
            self._client = None
            self._available = False


cache_service = CacheService()
