import json
import time
from typing import Any

try:
    import redis
except Exception:
    redis = None

from app.core.config import get_settings


class CacheBackend:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.memory: dict[str, tuple[float, Any]] = {}
        self.redis_client = None
        if self.settings.enable_redis and redis is not None:
            try:
                self.redis_client = redis.Redis.from_url(self.settings.redis_url, decode_responses=True)
                self.redis_client.ping()
            except Exception:
                self.redis_client = None

    def get(self, key: str) -> Any | None:
        if self.redis_client is not None:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        record = self.memory.get(key)
        if not record:
            return None
        expires_at, payload = record
        if expires_at < time.time():
            self.memory.pop(key, None)
            return None
        return payload

    def set(self, key: str, value: Any, ttl_seconds: int = 30) -> None:
        if self.redis_client is not None:
            self.redis_client.setex(key, ttl_seconds, json.dumps(value))
            return
        self.memory[key] = (time.time() + ttl_seconds, value)

    def delete_prefix(self, prefix: str) -> None:
        if self.redis_client is not None:
            for key in self.redis_client.scan_iter(f'{prefix}*'):
                self.redis_client.delete(key)
            return
        for key in list(self.memory.keys()):
            if key.startswith(prefix):
                self.memory.pop(key, None)


cache = CacheBackend()
