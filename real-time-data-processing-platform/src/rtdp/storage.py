from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


@dataclass(slots=True)
class Storage:
    db_path: Path

    def __post_init__(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init_db(self) -> None:
        with self.connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS entity_state (
                    entity_id TEXT PRIMARY KEY,
                    last_event_id TEXT NOT NULL,
                    event_count INTEGER NOT NULL,
                    last_event_type TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS processed_keys (
                    idempotency_key TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    processed_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS event_ledger (
                    event_id TEXT PRIMARY KEY,
                    entity_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    processed_at TEXT NOT NULL,
                    processing_latency_ms REAL NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS dlq (
                    dlq_id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    body_json TEXT NOT NULL,
                    attempts INTEGER NOT NULL,
                    last_error TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    replayed INTEGER NOT NULL DEFAULT 0
                );
                """
            )

    def is_duplicate(self, idempotency_key: str) -> bool:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM processed_keys WHERE idempotency_key = ?",
                (idempotency_key,),
            ).fetchone()
            return row is not None

    def mark_processed(self, event: dict[str, Any], latency_ms: float) -> bool:
        ts = datetime.now(timezone.utc).isoformat()
        with self.connection() as conn:
            existing = conn.execute(
                "SELECT 1 FROM processed_keys WHERE idempotency_key = ?",
                (event["idempotency_key"],),
            ).fetchone()
            if existing:
                return False
            conn.execute(
                "INSERT INTO processed_keys (idempotency_key, event_id, processed_at) VALUES (?, ?, ?)",
                (event["idempotency_key"], event["event_id"], ts),
            )
            conn.execute(
                "INSERT OR REPLACE INTO event_ledger (event_id, entity_id, event_type, processed_at, processing_latency_ms, payload_json) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    event["event_id"],
                    event["entity_id"],
                    event["event_type"],
                    ts,
                    latency_ms,
                    json.dumps(event["payload"], sort_keys=True),
                ),
            )
            current = conn.execute(
                "SELECT event_count, state_json FROM entity_state WHERE entity_id = ?",
                (event["entity_id"],),
            ).fetchone()
            prior_count = int(current["event_count"]) if current else 0
            state_json = current["state_json"] if current else "{}"
            state = json.loads(state_json)
            state["last_payload"] = event["payload"]
            state["last_event_type"] = event["event_type"]
            state["event_count"] = prior_count + 1
            if event["event_type"] == "purchase":
                state["last_amount"] = event["payload"].get("amount")
            conn.execute(
                "INSERT OR REPLACE INTO entity_state (entity_id, last_event_id, event_count, last_event_type, state_json, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    event["entity_id"],
                    event["event_id"],
                    prior_count + 1,
                    event["event_type"],
                    json.dumps(state, sort_keys=True),
                    ts,
                ),
            )
            return True

    def list_entities(self) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute("SELECT * FROM entity_state ORDER BY entity_id").fetchall()
            return [dict(row) for row in rows]

    def get_entity(self, entity_id: str) -> dict[str, Any] | None:
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM entity_state WHERE entity_id = ?", (entity_id,)).fetchone()
            return dict(row) if row else None

    def add_dlq(self, dlq_id: str, event: dict[str, Any], attempts: int, last_error: str) -> None:
        with self.connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO dlq (dlq_id, event_id, entity_id, body_json, attempts, last_error, created_at, replayed) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    dlq_id,
                    event["event_id"],
                    event["entity_id"],
                    json.dumps(event, sort_keys=True),
                    attempts,
                    last_error,
                    datetime.now(timezone.utc).isoformat(),
                    0,
                ),
            )

    def list_dlq(self) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute("SELECT * FROM dlq ORDER BY created_at").fetchall()
            return [dict(row) for row in rows]

    def get_dlq(self, dlq_id: str) -> dict[str, Any] | None:
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM dlq WHERE dlq_id = ?", (dlq_id,)).fetchone()
            return dict(row) if row else None

    def mark_dlq_replayed(self, dlq_id: str) -> None:
        with self.connection() as conn:
            conn.execute("UPDATE dlq SET replayed = 1 WHERE dlq_id = ?", (dlq_id,))
