import time
from collections.abc import Callable

from fastapi import Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
from starlette.routing import Route

REQUEST_COUNT = Counter(
    "service_platform_requests_total",
    "Total requests received",
    ["method", "path", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "service_platform_request_latency_seconds",
    "Latency by path",
    ["path"],
)
ACTIVE_REQUESTS = Gauge("service_platform_active_requests", "Active requests")
CIRCUIT_BREAKER_STATE = Gauge(
    "service_platform_circuit_breaker_state",
    "Circuit breaker state for downstream dependency. 0 closed, 1 open, 2 half_open",
)
DOWNSTREAM_CALLS = Counter(
    "service_platform_downstream_calls_total",
    "Downstream call results",
    ["outcome"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        ACTIVE_REQUESTS.inc()
        started = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            ACTIVE_REQUESTS.dec()
        elapsed = time.perf_counter() - started
        REQUEST_LATENCY.labels(request.url.path).observe(elapsed)
        REQUEST_COUNT.labels(request.method, request.url.path, getattr(response, "status_code", 500)).inc()
        return response


async def metrics_endpoint(_request):
    return StarletteResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


metrics_app = Starlette(routes=[Route("/", metrics_endpoint)])
metrics_app.add_middleware(MetricsMiddleware)
