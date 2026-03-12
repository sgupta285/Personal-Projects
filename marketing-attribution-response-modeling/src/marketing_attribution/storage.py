from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


def persist_to_sqlite(database_path: Path, tables: dict[str, pd.DataFrame]) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as conn:
        for name, df in tables.items():
            df.to_sql(name, conn, if_exists="replace", index=False)
