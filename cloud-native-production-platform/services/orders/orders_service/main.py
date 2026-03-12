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

import json
import sqlite3
from pathlib import Path

from fastapi import HTTPException
from pydantic import BaseModel

DB_PATH = Path(os.getenv("ORDER_DB_PATH", "/tmp/orders.db"))
_DB_LOCK = Lock()


class OrderIn(BaseModel):
    customer_id: str
    sku: str
    quantity: int


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _DB_LOCK:
        conn = _conn()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                sku TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        conn.close()


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    started = time.perf_counter()
    payload = {"status": "ok", "service": SERVICE_NAME, "db_path": str(DB_PATH)}
    observe_request("GET", "/health", started)
    return payload


@app.get("/orders")
def list_orders() -> dict:
    started = time.perf_counter()
    with _DB_LOCK:
        conn = _conn()
        rows = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
        conn.close()
    orders = [dict(row) for row in rows]
    observe_request("GET", "/orders", started)
    return {"orders": orders}


@app.post("/orders")
def create_order(order: OrderIn) -> dict:
    started = time.perf_counter()
    if order.quantity <= 0:
        raise HTTPException(status_code=400, detail="quantity must be positive")

    with _DB_LOCK:
        conn = _conn()
        cursor = conn.execute(
            "INSERT INTO orders(customer_id, sku, quantity, status) VALUES (?, ?, ?, ?)",
            (order.customer_id, order.sku, order.quantity, "created"),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM orders WHERE id = ?", (cursor.lastrowid,)).fetchone()
        conn.close()
    payload = {"order": dict(row)}
    observe_request("POST", "/orders", started)
    return payload
