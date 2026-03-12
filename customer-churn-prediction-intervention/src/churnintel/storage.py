from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


def seed_sqlite_database(raw_df: pd.DataFrame, feature_df: pd.DataFrame, database_url: str) -> None:
    if database_url.startswith("sqlite:///"):
        db_path = Path(database_url.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(database_url)
    with engine.begin() as connection:
        raw_df.to_sql("raw_customer_events", connection, if_exists="replace", index=False)
        feature_df.to_sql("customer_features", connection, if_exists="replace", index=False)
