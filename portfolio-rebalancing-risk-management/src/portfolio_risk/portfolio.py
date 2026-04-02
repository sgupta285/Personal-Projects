from __future__ import annotations

import pandas as pd


def latest_prices(prices: pd.DataFrame) -> pd.DataFrame:
    latest_date = prices["date"].max()
    snapshot = prices.loc[prices["date"] == latest_date, ["ticker", "close"]].copy()
    return snapshot


def portfolio_snapshot(prices: pd.DataFrame, positions: pd.DataFrame, targets: pd.DataFrame) -> pd.DataFrame:
    latest = latest_prices(prices)
    snapshot = positions.merge(latest, on="ticker", how="inner").merge(targets, on="ticker", how="left")
    snapshot["market_value"] = snapshot["shares"] * snapshot["close"]
    total_value = snapshot["market_value"].sum()
    snapshot["current_weight"] = snapshot["market_value"] / total_value
    snapshot["weight_drift"] = snapshot["current_weight"] - snapshot["target_weight"]
    snapshot["drift_bps"] = snapshot["weight_drift"] * 10000
    return snapshot.sort_values("ticker").reset_index(drop=True)
