import hashlib
import json
from collections.abc import Callable
from typing import Any

try:
    import redis
except Exception:  # pragma: no cover
    redis = None

from app.core.config import get_settings


class CacheService:
    def __init__(self) -> None:
        settings = get_settings()
        self.ttl = settings.cache_ttl_seconds
        self._client = None
        if settings.redis_url and redis is not None:
            try:
                self._client = redis.from_url(settings.redis_url, decode_responses=True)
                self._client.ping()
            except Exception:
                self._client = None
        self._memory: dict[str, str] = {}

    @staticmethod
    def build_key(prefix: str, payload: dict[str, Any]) -> str:
        encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return f"{prefix}:{hashlib.sha256(encoded).hexdigest()}"

    def get_json(self, key: str) -> dict[str, Any] | None:
        if self._client is not None:
            value = self._client.get(key)
            return json.loads(value) if value else None
        value = self._memory.get(key)
        return json.loads(value) if value else None

    def set_json(self, key: str, value: dict[str, Any]) -> None:
        payload = json.dumps(value, default=str)
        if self._client is not None:
            self._client.setex(key, self.ttl, payload)
        else:
            self._memory[key] = payload

    def remember(self, prefix: str, payload: dict[str, Any], fn: Callable[[], dict[str, Any]]) -> dict[str, Any]:
        key = self.build_key(prefix, payload)
        cached = self.get_json(key)
        if cached is not None:
            return cached
        value = fn()
        self.set_json(key, value)
        return value


cache_service = CacheService()
