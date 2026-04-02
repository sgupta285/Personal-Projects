from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(slots=True)
class ExecutionParams:
    tier: str
    commission_per_share: float
    spread_bps: float
    route_fee_bps: float
    latency_ms: float
    annual_borrow_bps: float = 0.0


TIER_MULTIPLIER = {
    "M0": 0.0,
    "M1": 0.35,
    "M2": 0.65,
    "M3": 1.0,
    "M4": 1.35,
    "M5": 1.75,
}


def apply_execution_model(trades: pd.DataFrame, market: pd.DataFrame, params: ExecutionParams) -> pd.DataFrame:
    merged = trades.merge(
        market[["date", "ticker", "close", "volume", "daily_vol_bps"]],
        on=["date", "ticker"],
        how="left",
        validate="many_to_one",
    )
    merged["volume"] = merged["volume"].replace(0, np.nan).ffill().fillna(1.0)
    participation = (merged["shares"].abs() / merged["volume"]).clip(lower=0.0, upper=1.0)
    multiplier = TIER_MULTIPLIER[params.tier]
    spread_cost = merged["close"] * merged["shares"].abs() * (params.spread_bps / 10000.0) * 0.5 * multiplier
    impact_cost = merged["close"] * merged["shares"].abs() * (
        0.25 * np.sqrt(participation) + 0.15 * (merged["daily_vol_bps"] / 10000.0)
    ) * multiplier
    latency_cost = merged["close"] * merged["shares"].abs() * (merged["daily_vol_bps"] / 10000.0) * (params.latency_ms / 1000.0) * 0.05 * multiplier
    route_fee = merged["close"] * merged["shares"].abs() * (params.route_fee_bps / 10000.0) * multiplier
    commission = merged["shares"].abs() * params.commission_per_share
    borrow_cost = merged["close"] * merged["short_inventory"].clip(lower=0.0) * (params.annual_borrow_bps / 10000.0) / 252.0 * multiplier

    merged["transaction_cost"] = spread_cost + impact_cost + latency_cost + route_fee + commission + borrow_cost
    signed_slippage = np.sign(merged["shares"]).replace(0, 1.0) * merged["transaction_cost"] / merged["shares"].abs().replace(0, np.nan)
    merged["fill_price"] = merged["close"] + signed_slippage.fillna(0.0)
    return merged
