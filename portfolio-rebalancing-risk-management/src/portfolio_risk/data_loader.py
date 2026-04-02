from __future__ import annotations

from pathlib import Path
import pandas as pd


def load_prices(path: str | Path) -> pd.DataFrame:
    prices = pd.read_csv(path, parse_dates=["date"])
    required = {"date", "ticker", "close"}
    missing = required - set(prices.columns)
    if missing:
        raise ValueError(f"prices file missing columns: {sorted(missing)}")
    prices = prices.sort_values(["date", "ticker"]).reset_index(drop=True)
    return prices


def load_positions(path: str | Path) -> pd.DataFrame:
    positions = pd.read_csv(path)
    required = {"ticker", "shares", "lot_cost"}
    missing = required - set(positions.columns)
    if missing:
        raise ValueError(f"positions file missing columns: {sorted(missing)}")
    return positions


def load_targets(path: str | Path) -> pd.DataFrame:
    targets = pd.read_csv(path)
    required = {"ticker", "asset_class", "target_weight"}
    missing = required - set(targets.columns)
    if missing:
        raise ValueError(f"targets file missing columns: {sorted(missing)}")
    weight_sum = targets["target_weight"].sum()
    if abs(weight_sum - 1.0) > 1e-6:
        raise ValueError(f"target weights must sum to 1.0, found {weight_sum:.6f}")
    return targets
