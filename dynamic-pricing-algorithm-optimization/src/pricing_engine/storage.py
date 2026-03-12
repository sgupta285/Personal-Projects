from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


def seed_database(catalog: pd.DataFrame, transactions: pd.DataFrame, features: pd.DataFrame, database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as conn:
        catalog.to_sql("product_catalog", conn, if_exists="replace", index=False)
        transactions.to_sql("transactions", conn, if_exists="replace", index=False)
        features.to_sql("pricing_features", conn, if_exists="replace", index=False)


def run_sql_query(database_path: Path, sql_text: str) -> pd.DataFrame:
    with sqlite3.connect(database_path) as conn:
        return pd.read_sql_query(sql_text, conn)
