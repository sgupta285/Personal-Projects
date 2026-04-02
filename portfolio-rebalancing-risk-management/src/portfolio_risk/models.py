from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RiskSnapshot:
    portfolio_value: float
    daily_var: float
    daily_cvar: float
    annualized_volatility: float
    sharpe_ratio: float


@dataclass(slots=True)
class RebalanceTrade:
    ticker: str
    current_weight: float
    target_weight: float
    recommended_weight: float
    trade_value: float
    action: str


@dataclass(slots=True)
class EfficientFrontierPoint:
    expected_return: float
    annualized_volatility: float
    weights: dict[str, float]
