from __future__ import annotations

from pathlib import Path
import sqlite3
import pandas as pd

from ecomopt.config import settings

SQL_DIR = Path(__file__).resolve().parents[2] / "sql"


def _sqlite_path(database_url: str) -> Path:
    if database_url.startswith("sqlite:///"):
        return Path(database_url.replace("sqlite:///", ""))
    raise ValueError("Only sqlite URLs are supported in the local repo setup")


def seed_database(database_url: str, sessions: pd.DataFrame, events: pd.DataFrame) -> None:
    db_path = _sqlite_path(database_url)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        sessions.to_sql("raw_sessions", conn, if_exists="replace", index=False)
        events.to_sql("raw_events", conn, if_exists="replace", index=False)
    finally:
        conn.close()


def export_sql_models(database_url: str) -> dict[str, pd.DataFrame]:
    db_path = _sqlite_path(database_url)
    conn = sqlite3.connect(db_path)
    try:
        queries = {
            "funnel_stage_metrics": (SQL_DIR / "funnel_stage_metrics.sql").read_text(),
            "experiment_cohorts": (SQL_DIR / "experiment_cohorts.sql").read_text(),
            "funnel_segment_metrics": (SQL_DIR / "funnel_segment_metrics.sql").read_text(),
        }
        outputs = {name: pd.read_sql_query(query, conn) for name, query in queries.items()}
    finally:
        conn.close()
    outputs["funnel_stage_metrics"].to_csv(settings.stage_metrics_path, index=False)
    outputs["experiment_cohorts"].to_csv(settings.experiment_cohorts_path, index=False)
    outputs["funnel_segment_metrics"].to_csv(settings.segment_metrics_path, index=False)
    return outputs
