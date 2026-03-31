from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.config import settings


def _resolve_sqlite_path(database_url: str) -> Path:
    if not database_url.startswith("sqlite:///"):
        raise ValueError("Only sqlite:/// URLs are supported in the starter template.")
    raw = database_url.replace("sqlite:///", "", 1)
    return Path(raw)


DB_PATH = _resolve_sqlite_path(settings.database_url)


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS datasets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    task_family TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS preference_examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_id INTEGER NOT NULL,
    prompt_text TEXT NOT NULL,
    task_type TEXT NOT NULL,
    context_json TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    example_id INTEGER NOT NULL,
    label TEXT NOT NULL,
    response_text TEXT NOT NULL,
    model_name TEXT,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(example_id) REFERENCES preference_examples(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    example_id INTEGER NOT NULL,
    annotator_id TEXT NOT NULL,
    winner_candidate_id INTEGER,
    ranking_json TEXT NOT NULL,
    notes TEXT,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(example_id) REFERENCES preference_examples(id) ON DELETE CASCADE,
    FOREIGN KEY(winner_candidate_id) REFERENCES candidates(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS reward_targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    example_id INTEGER NOT NULL UNIQUE,
    targets_json TEXT NOT NULL,
    method TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(example_id) REFERENCES preference_examples(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS dataset_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_id INTEGER NOT NULL,
    version_name TEXT NOT NULL,
    manifest_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(dataset_id, version_name),
    FOREIGN KEY(dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS experiment_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_id INTEGER NOT NULL,
    snapshot_id INTEGER,
    name TEXT NOT NULL,
    config_json TEXT NOT NULL,
    metrics_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
    FOREIGN KEY(snapshot_id) REFERENCES dataset_snapshots(id) ON DELETE SET NULL
);
"""


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA_SQL)


def dumps(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True)
