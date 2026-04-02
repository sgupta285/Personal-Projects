from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from app.config import settings


def _db_path() -> Path:
    raw = settings.database_url
    if raw.startswith("sqlite:///"):
        return Path(raw.removeprefix("sqlite:///"))
    raise ValueError("Only sqlite:/// URLs are supported for local development")


@contextmanager
def get_conn() -> Iterable[sqlite3.Connection]:
    db_path = _db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                org_id TEXT NOT NULL,
                mfa_secret TEXT NOT NULL,
                can_use_mfa INTEGER NOT NULL DEFAULT 1,
                allowed_tags TEXT NOT NULL DEFAULT '[]',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id_hash TEXT NOT NULL,
                org_id TEXT NOT NULL,
                classification TEXT NOT NULL,
                region TEXT NOT NULL,
                department TEXT NOT NULL,
                kms_key_id TEXT NOT NULL,
                encrypted_payload TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_records_org ON records(org_id);
            CREATE INDEX IF NOT EXISTS idx_records_subject_hash ON records(subject_id_hash);
            CREATE INDEX IF NOT EXISTS idx_records_region ON records(region);

            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                resource TEXT NOT NULL,
                status TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                prev_hash TEXT NOT NULL,
                entry_hash TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS key_rotations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                old_key_id TEXT NOT NULL,
                new_key_id TEXT NOT NULL,
                rotated_at TEXT NOT NULL,
                records_reencrypted INTEGER NOT NULL
            );
            """
        )


def fetch_one(query: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute(query, params).fetchone()


def fetch_all(query: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return list(conn.execute(query, params).fetchall())


def execute(query: str, params: tuple[Any, ...] = ()) -> int:
    with get_conn() as conn:
        cur = conn.execute(query, params)
        return int(cur.lastrowid)
