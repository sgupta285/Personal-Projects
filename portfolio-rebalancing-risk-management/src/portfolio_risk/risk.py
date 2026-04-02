from __future__ import annotations

import numpy as np
import pandas as pd

from .models import RiskSnapshot


def return_matrix(prices: pd.DataFrame) -> pd.DataFrame:
    wide = prices.pivot(index="date", columns="ticker", values="close").sort_index()
    returns = wide.pct_change().dropna(how="all")
    return returns


def position_weights(snapshot: pd.DataFrame) -> pd.Series:
    return snapshot.set_index("ticker")["current_weight"].sort_index()


def expected_asset_returns(returns: pd.DataFrame, annualization: int = 252) -> pd.Series:
    return returns.mean() * annualization


def covariance_matrix(returns: pd.DataFrame, annualization: int = 252) -> pd.DataFrame:
    return returns.cov() * annualization


def historical_var(series: pd.Series, confidence: float = 0.95) -> float:
    percentile = np.percentile(series, (1.0 - confidence) * 100.0)
    return float(-percentile)


def historical_cvar(series: pd.Series, confidence: float = 0.95) -> float:
    threshold = np.percentile(series, (1.0 - confidence) * 100.0)
    tail = series[series <= threshold]
    if tail.empty:
        return 0.0
    return float(-tail.mean())


def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    return returns.corr()


def portfolio_returns(returns: pd.DataFrame, snapshot: pd.DataFrame) -> pd.Series:
    weights = position_weights(snapshot).reindex(returns.columns).fillna(0.0)
    weighted = returns.mul(weights, axis=1)
    return weighted.sum(axis=1)


def risk_snapshot(returns: pd.DataFrame, snapshot: pd.DataFrame, risk_free_rate: float, confidence: float, annualization: int = 252) -> RiskSnapshot:
    port = portfolio_returns(returns, snapshot)
    ann_vol = float(port.std(ddof=1) * np.sqrt(annualization))
    excess_return = float(port.mean() * annualization - risk_free_rate)
    sharpe = excess_return / ann_vol if ann_vol > 0 else 0.0
    total_value = float(snapshot["market_value"].sum())
    return RiskSnapshot(
        portfolio_value=total_value,
        daily_var=historical_var(port, confidence),
        daily_cvar=historical_cvar(port, confidence),
        annualized_volatility=ann_vol,
        sharpe_ratio=sharpe,
    )
