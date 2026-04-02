from contextlib import contextmanager
from time import perf_counter

from prometheus_client import Counter, Histogram


REQUESTS = Counter("reco_requests_total", "Total recommendation requests", ["surface"])
CACHE_HITS = Counter("reco_cache_hits_total", "Recommendation cache hits")
LATENCY = Histogram("reco_request_latency_seconds", "Recommendation request latency", ["surface"])


class Metrics:
    @contextmanager
    def request_timer(self, surface: str):
        REQUESTS.labels(surface=surface).inc()
        start = perf_counter()
        try:
            yield
        finally:
            LATENCY.labels(surface=surface).observe(perf_counter() - start)


metrics = Metrics()
