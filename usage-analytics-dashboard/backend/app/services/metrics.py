from time import perf_counter

from fastapi import Request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

REQUEST_COUNT = Counter("usage_dashboard_requests_total", "Total API requests", ["method", "path", "status_code"])
REQUEST_LATENCY = Histogram("usage_dashboard_request_latency_seconds", "API latency", ["method", "path"])
CACHE_HITS = Counter("usage_dashboard_cache_hits_total", "Cache hits", ["endpoint"])
CACHE_MISSES = Counter("usage_dashboard_cache_misses_total", "Cache misses", ["endpoint"])


async def metrics_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


async def metrics_middleware(request: Request, call_next):
    start = perf_counter()
    response = await call_next(request)
    elapsed = perf_counter() - start
    REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.method, request.url.path).observe(elapsed)
    return response
