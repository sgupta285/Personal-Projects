import json
import random
import time

from fastapi import HTTPException

from app.core.config import get_settings
from app.observability.metrics import DOWNSTREAM_CALLS
from app.services.circuit_breaker import service_circuit_breaker

settings = get_settings()


def process_downstream(payload: dict, force_fail: bool = False) -> float:
    if not service_circuit_breaker.allow_request():
        DOWNSTREAM_CALLS.labels("circuit_open").inc()
        raise HTTPException(status_code=503, detail="Downstream dependency unavailable")

    started = time.perf_counter()
    base = settings.downstream_base_latency_ms
    jitter = settings.downstream_jitter_ms
    sleep_for = max(0, (base + random.randint(0, jitter)) / 1000)
    time.sleep(sleep_for)

    if force_fail or payload.get("simulate_failure"):
        service_circuit_breaker.mark_failure()
        DOWNSTREAM_CALLS.labels("failure").inc()
        raise HTTPException(status_code=502, detail="Downstream call failed")

    json.dumps(payload)
    service_circuit_breaker.mark_success()
    DOWNSTREAM_CALLS.labels("success").inc()
    return round((time.perf_counter() - started) * 1000, 2)
