from __future__ import annotations

import pandas as pd

from .models import RebalanceTrade


def generate_rebalancing_plan(snapshot: pd.DataFrame, optimized_weights: pd.Series, drift_threshold_bps: float = 75.0) -> list[RebalanceTrade]:
    total_value = float(snapshot["market_value"].sum())
    rows: list[RebalanceTrade] = []
    for _, row in snapshot.iterrows():
        ticker = row["ticker"]
        current_weight = float(row["current_weight"])
        target_weight = float(row["target_weight"])
        recommended_weight = float(optimized_weights.get(ticker, target_weight))
        trade_value = (recommended_weight - current_weight) * total_value
        if abs(row["drift_bps"]) < drift_threshold_bps and abs(trade_value) < total_value * 0.005:
            continue
        action = "buy" if trade_value > 0 else "sell"
        rows.append(
            RebalanceTrade(
                ticker=ticker,
                current_weight=current_weight,
                target_weight=target_weight,
                recommended_weight=recommended_weight,
                trade_value=trade_value,
                action=action,
            )
        )
    return sorted(rows, key=lambda trade: abs(trade.trade_value), reverse=True)
