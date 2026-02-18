"""
Simple in-memory rate limiter using sliding window counter.
"""

import time
import threading
from collections import defaultdict
from fastapi import Request, HTTPException

from app.config import settings


class RateLimiter:
    def __init__(self, max_requests: int = settings.rate_limit_per_minute, window_seconds: int = 60):
        self._max_requests = max_requests
        self._window = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def _get_client_id(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def check(self, request: Request) -> bool:
        client_id = self._get_client_id(request)
        now = time.time()
        cutoff = now - self._window

        with self._lock:
            # Remove expired entries
            self._requests[client_id] = [t for t in self._requests[client_id] if t > cutoff]

            if len(self._requests[client_id]) >= self._max_requests:
                return False

            self._requests[client_id].append(now)
            return True

    def get_remaining(self, request: Request) -> int:
        client_id = self._get_client_id(request)
        now = time.time()
        cutoff = now - self._window

        with self._lock:
            active = [t for t in self._requests.get(client_id, []) if t > cutoff]
            return max(0, self._max_requests - len(active))


rate_limiter = RateLimiter()
