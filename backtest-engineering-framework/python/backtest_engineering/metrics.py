from __future__ import annotations

import math
from typing import Iterable

import numpy as np
import pandas as pd
from scipy import stats


TRADING_DAYS = 252


def annualized_return(returns: pd.Series) -> float:
    compounded = float((1.0 + returns).prod())
    periods = max(len(returns), 1)
    return compounded ** (TRADING_DAYS / periods) - 1.0


def annualized_volatility(returns: pd.Series) -> float:
    return float(returns.std(ddof=1) * math.sqrt(TRADING_DAYS)) if len(returns) > 1 else 0.0


def sharpe_ratio(returns: pd.Series) -> float:
    vol = annualized_volatility(returns)
    if vol == 0.0:
        return 0.0
    return annualized_return(returns) / vol


def max_drawdown(equity_curve: pd.Series) -> float:
    running_max = equity_curve.cummax()
    drawdown = equity_curve / running_max - 1.0
    return float(drawdown.min())


def jobson_korkie_t_stat(returns: pd.Series) -> float:
    mean = returns.mean()
    std = returns.std(ddof=1)
    if std == 0 or np.isnan(std):
        return 0.0
    return float((mean / std) * math.sqrt(len(returns)))


def p_value_from_tstat(t_stat: float, df: int) -> float:
    if df <= 0:
        return 1.0
    return float(2 * (1 - stats.t.cdf(abs(t_stat), df=df)))


def holm_bonferroni(p_values: Iterable[float]) -> list[float]:
    indexed = sorted(enumerate(p_values), key=lambda item: item[1])
    adjusted = [0.0] * len(indexed)
    total = len(indexed)
    running_max = 0.0
    for rank, (original_idx, p_val) in enumerate(indexed):
        candidate = min(1.0, (total - rank) * p_val)
        running_max = max(running_max, candidate)
        adjusted[original_idx] = running_max
    return adjusted
