from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "date",
    "ticker",
    "open",
    "high",
    "low",
    "close",
    "volume",
}


def load_prices(path: str | Path, tickers: list[str] | None = None) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    if tickers:
        df = df[df["ticker"].isin(tickers)].copy()
    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)
    return df
