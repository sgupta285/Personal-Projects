import time
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import get_settings


class TokenBucket:
    def __init__(self, capacity: int, refill_per_second: int):
        self.capacity = capacity
        self.refill_per_second = refill_per_second
        self.buckets: dict[str, tuple[float, float]] = {}

    def consume(self, key: str, tokens: float = 1) -> bool:
        now = time.monotonic()
        balance, last = self.buckets.get(key, (self.capacity, now))
        balance = min(self.capacity, balance + (now - last) * self.refill_per_second)
        if balance < tokens:
            self.buckets[key] = (balance, now)
            return False
        self.buckets[key] = (balance - tokens, now)
        return True


settings = get_settings()
token_bucket = TokenBucket(settings.rate_limit_capacity, settings.rate_limit_refill_per_second)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        client_ip = request.client.host if request.client else "unknown"
        user_key = request.headers.get("authorization", "anonymous")
        composite_key = f"{client_ip}:{user_key}"
        if not token_bucket.consume(composite_key):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
            )
        return await call_next(request)
