"""
Rate limiting middleware using Redis sliding window.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.services.redis_service import redis_service
from app.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health and docs
        if request.url.path in ("/health", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not client_ip:
            client_ip = request.client.host if request.client else "unknown"

        allowed, remaining = redis_service.check_rate_limit(client_ip)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded", "retry_after": settings.redis_rate_limit_window},
                headers={
                    "X-RateLimit-Limit": str(settings.redis_rate_limit_max),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": str(settings.redis_rate_limit_window),
                },
            )

        response: Response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(settings.redis_rate_limit_max)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
