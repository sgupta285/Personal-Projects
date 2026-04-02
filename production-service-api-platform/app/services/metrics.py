import time
from collections import Counter, defaultdict
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter as PromCounter, Histogram, generate_latest


registry = CollectorRegistry()
request_counter = PromCounter('http_requests_total', 'Request count', ['path', 'method', 'status_code'], registry=registry)
request_latency = Histogram('http_request_duration_seconds', 'Request latency', ['path', 'method'], registry=registry)
client_counter = Counter()
endpoint_errors = defaultdict(int)


def record_request(path: str, method: str, status_code: int, duration: float, client_id: str | None = None) -> None:
    request_counter.labels(path=path, method=method, status_code=str(status_code)).inc()
    request_latency.labels(path=path, method=method).observe(duration)
    if client_id:
        client_counter[client_id] += 1
    if status_code >= 400:
        endpoint_errors[(path, status_code)] += 1


def render_metrics() -> tuple[bytes, str]:
    return generate_latest(registry), CONTENT_TYPE_LATEST
