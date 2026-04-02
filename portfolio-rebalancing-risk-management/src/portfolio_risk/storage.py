from __future__ import annotations

import sqlite3
from pathlib import Path
from urllib.parse import urlparse

from .models import RiskSnapshot


def sqlite_path_from_url(database_url: str) -> str:
    if database_url.startswith("sqlite:///"):
        return database_url.replace("sqlite:///", "", 1)
    if database_url.startswith("postgresql://"):
        return "artifacts/demo/portfolio_shadow.db"
    return database_url


def ensure_sqlite(database_url: str) -> sqlite3.Connection:
    path = Path(sqlite_path_from_url(database_url))
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS risk_snapshots (
            snapshot_date TEXT PRIMARY KEY,
            portfolio_value REAL NOT NULL,
            daily_var REAL NOT NULL,
            daily_cvar REAL NOT NULL,
            volatility REAL NOT NULL,
            sharpe_ratio REAL NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def persist_risk_snapshot(snapshot_date: str, snapshot: RiskSnapshot, database_url: str) -> None:
    conn = ensure_sqlite(database_url)
    with conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO risk_snapshots (
                snapshot_date,
                portfolio_value,
                daily_var,
                daily_cvar,
                volatility,
                sharpe_ratio
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot_date,
                snapshot.portfolio_value,
                snapshot.daily_var,
                snapshot.daily_cvar,
                snapshot.annualized_volatility,
                snapshot.sharpe_ratio,
            ),
        )
    conn.close()
