from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .execution import ExecutionParams, apply_execution_model
from .metrics import annualized_return, annualized_volatility, max_drawdown, p_value_from_tstat, sharpe_ratio, jobson_korkie_t_stat
from .strategy import build_signals


@dataclass(slots=True)
class BacktestResult:
    portfolio_returns: pd.Series
    equity_curve: pd.Series
    trade_log: pd.DataFrame
    summary: dict[str, float]



def run_backtest(
    prices: pd.DataFrame,
    execution_params: ExecutionParams,
    short_window: int,
    long_window: int,
    volatility_lookback: int,
    target_gross_leverage: float,
    initial_capital: float,
) -> BacktestResult:
    signals = build_signals(prices, short_window, long_window, volatility_lookback, target_gross_leverage)
    weights = signals[["date", "ticker", "weight"]].copy()
    weights["target_weight_prev"] = weights.groupby("ticker")["weight"].shift(1).fillna(0.0)
    weights["delta_weight"] = weights["weight"] - weights["target_weight_prev"]

    prices_with_vol = prices.copy()
    prices_with_vol["ret"] = prices_with_vol.groupby("ticker")["close"].pct_change().fillna(0.0)
    prices_with_vol["daily_vol_bps"] = (
        prices_with_vol.groupby("ticker")["ret"]
        .transform(lambda s: s.rolling(volatility_lookback).std())
        .fillna(0.0)
        * 10000.0
    )

    turnover = weights.merge(prices_with_vol[["date", "ticker", "close", "volume", "daily_vol_bps"]], on=["date", "ticker"], how="left")
    turnover["notional"] = turnover["delta_weight"].abs() * initial_capital
    turnover["shares"] = np.where(turnover["close"] > 0, turnover["notional"] / turnover["close"], 0.0)
    turnover["short_inventory"] = np.where(turnover["weight"] < 0, turnover["shares"].abs(), 0.0)

    trade_log = apply_execution_model(
        turnover[["date", "ticker", "shares", "short_inventory"]],
        prices_with_vol,
        execution_params,
    )

    signal_returns = signals[["date", "ticker", "weight", "ret"]].copy()
    signal_returns["prev_weight"] = signal_returns.groupby("ticker")["weight"].shift(1).fillna(0.0)
    signal_returns["strategy_ret"] = signal_returns["prev_weight"] * signal_returns["ret"]
    gross_returns = signal_returns.groupby("date")["strategy_ret"].sum().sort_index()
    costs_by_day = trade_log.groupby("date")["transaction_cost"].sum().sort_index() / initial_capital
    portfolio_returns = gross_returns.sub(costs_by_day, fill_value=0.0)
    equity_curve = (1.0 + portfolio_returns).cumprod() * initial_capital

    t_stat = jobson_korkie_t_stat(portfolio_returns)
    summary = {
        "annualized_return": annualized_return(portfolio_returns),
        "annualized_volatility": annualized_volatility(portfolio_returns),
        "sharpe_ratio": sharpe_ratio(portfolio_returns),
        "max_drawdown": max_drawdown(equity_curve),
        "turnover_dollars": float(turnover["notional"].sum()),
        "transaction_cost_dollars": float(trade_log["transaction_cost"].sum()),
        "t_stat": t_stat,
        "p_value": p_value_from_tstat(t_stat, max(len(portfolio_returns) - 1, 1)),
    }
    return BacktestResult(
        portfolio_returns=portfolio_returns,
        equity_curve=equity_curve,
        trade_log=trade_log,
        summary=summary,
    )
