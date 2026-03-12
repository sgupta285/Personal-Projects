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

import httpx
from fastapi import HTTPException
from pydantic import BaseModel

CATALOG_URL = os.getenv("CATALOG_URL", "http://localhost:8001")
ORDERS_URL = os.getenv("ORDERS_URL", "http://localhost:8002")


class OrderIn(BaseModel):
    customer_id: str
    sku: str
    quantity: int


async def _get_json(url: str) -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


async def _post_json(url: str, payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


@app.get("/health")
async def health() -> dict:
    started = time.perf_counter()
    try:
        catalog = await _get_json(f"{CATALOG_URL}/health")
        orders = await _get_json(f"{ORDERS_URL}/health")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"dependency check failed: {exc}") from exc

    payload = {"status": "ok", "service": SERVICE_NAME, "dependencies": {"catalog": catalog, "orders": orders}}
    observe_request("GET", "/health", started)
    return payload


@app.get("/products")
async def products() -> dict:
    started = time.perf_counter()
    data = await _get_json(f"{CATALOG_URL}/products")
    observe_request("GET", "/products", started)
    return data


@app.post("/orders")
async def orders(order: OrderIn) -> dict:
    started = time.perf_counter()
    data = await _post_json(f"{ORDERS_URL}/orders", order.model_dump())
    observe_request("POST", "/orders", started)
    return data
