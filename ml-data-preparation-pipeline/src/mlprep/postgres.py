from __future__ import annotations

import os

import pandas as pd
from sqlalchemy import create_engine, text


def build_postgres_url() -> str:
    return (
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER', 'ml_user')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'ml_password')}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'ml_prep')}"
    )


def export_dataframe(df: pd.DataFrame, table_name: str, schema: str = "analytics") -> None:
    engine = create_engine(build_postgres_url())
    with engine.begin() as connection:
        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
    df.to_sql(table_name, engine, schema=schema, if_exists="replace", index=False)
