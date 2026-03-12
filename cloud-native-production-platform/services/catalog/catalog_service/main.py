from __future__ import annotations

import os
import time
from threading import Lock

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import CollectorRegistry, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

SERVICE_NAME = os.getenv("SERVICE_NAME", "service")

app = FastAPI(title=f"{SERVICE_NAME.title()} Service")
registry = CollectorRegistry()
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Request count",
    ["service", "method", "path"],
    registry=registry,
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency",
    ["service", "method", "path"],
    registry=registry,
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5),
)


def observe_request(method: str, path: str, started: float) -> None:
    duration = time.perf_counter() - started
    REQUEST_COUNT.labels(SERVICE_NAME, method, path).inc()
    REQUEST_LATENCY.labels(SERVICE_NAME, method, path).observe(duration)


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest(registry).decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


PRODUCTS = [
    {"sku": "sku-101", "name": "Telemetry Mug", "price": 18.0, "inventory": 52},
    {"sku": "sku-102", "name": "Platform Notebook", "price": 12.5, "inventory": 31},
    {"sku": "sku-103", "name": "Ops Hoodie", "price": 54.0, "inventory": 14},
]


@app.get("/health")
def health() -> dict:
    started = time.perf_counter()
    payload = {"status": "ok", "service": SERVICE_NAME, "items": len(PRODUCTS)}
    observe_request("GET", "/health", started)
    return payload


@app.get("/products")
def list_products() -> dict:
    started = time.perf_counter()
    payload = {"products": PRODUCTS}
    observe_request("GET", "/products", started)
    return payload
