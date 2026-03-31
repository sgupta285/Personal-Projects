from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable

from app.config import settings


def _dict_factory(cursor: sqlite3.Cursor, row: tuple[Any, ...]) -> dict[str, Any]:
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def ensure_parent_dir() -> None:
    db_file = Path(settings.database_path)
    if db_file.parent != Path('.'):
        db_file.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_connection() -> Iterable[sqlite3.Connection]:
    ensure_parent_dir()
    conn = sqlite3.connect(settings.database_path, check_same_thread=False)
    conn.row_factory = _dict_factory
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                role TEXT NOT NULL,
                skill_level TEXT DEFAULT 'general',
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',
                priority INTEGER DEFAULT 50,
                batch_name TEXT,
                requires_review INTEGER DEFAULT 1,
                seed_task INTEGER DEFAULT 0,
                payload_json TEXT NOT NULL,
                gold_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'assigned',
                assigned_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                UNIQUE(task_id, user_id),
                FOREIGN KEY(task_id) REFERENCES tasks(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assignment_id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                response_json TEXT NOT NULL,
                quality_flags_json TEXT,
                time_spent_seconds INTEGER DEFAULT 0,
                submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(assignment_id) REFERENCES assignments(id),
                FOREIGN KEY(task_id) REFERENCES tasks(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                response_id INTEGER NOT NULL,
                reviewer_id INTEGER NOT NULL,
                decision TEXT NOT NULL,
                score REAL DEFAULT 0,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(response_id) REFERENCES responses(id),
                FOREIGN KEY(reviewer_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS task_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(task_id) REFERENCES tasks(id)
            );
            """
        )


def dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)


def loads(data: str | None) -> Any:
    if not data:
        return None
    return json.loads(data)
