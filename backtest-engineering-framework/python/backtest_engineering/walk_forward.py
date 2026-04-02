from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import pandas as pd

from .engine import BacktestResult, run_backtest
from .execution import ExecutionParams
from .metrics import holm_bonferroni


@dataclass(slots=True)
class WalkForwardOutput:
    fold_results: list[dict]
    leaderboard: pd.DataFrame
    best_params: dict[str, int]
    stitched_result: BacktestResult



def _date_windows(dates: list[pd.Timestamp], train_days: int, test_days: int, step_days: int) -> list[tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp, pd.Timestamp]]:
    windows: list[tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp, pd.Timestamp]] = []
    idx = 0
    while idx + train_days + test_days <= len(dates):
        train_start = dates[idx]
        train_end = dates[idx + train_days - 1]
        test_start = dates[idx + train_days]
        test_end = dates[idx + train_days + test_days - 1]
        windows.append((train_start, train_end, test_start, test_end))
        idx += step_days
    return windows



def run_walk_forward(
    prices: pd.DataFrame,
    execution_params: ExecutionParams,
    sweep_short_windows: list[int],
    sweep_long_windows: list[int],
    volatility_lookback: int,
    target_gross_leverage: float,
    train_days: int,
    test_days: int,
    step_days: int,
    initial_capital: float,
) -> WalkForwardOutput:
    unique_dates = sorted(prices["date"].unique().tolist())
    windows = _date_windows(unique_dates, train_days, test_days, step_days)
    fold_results: list[dict] = []
    stitched_returns: list[pd.Series] = []
    stitched_trades: list[pd.DataFrame] = []

    for train_start, train_end, test_start, test_end in windows:
        train = prices[(prices["date"] >= train_start) & (prices["date"] <= train_end)].copy()
        test = prices[(prices["date"] >= test_start) & (prices["date"] <= test_end)].copy()
        candidates: list[dict] = []
        for short_window, long_window in product(sweep_short_windows, sweep_long_windows):
            if short_window >= long_window:
                continue
            result = run_backtest(
                train,
                execution_params,
                short_window,
                long_window,
                volatility_lookback,
                target_gross_leverage,
                initial_capital,
            )
            candidates.append({
                "short_window": short_window,
                "long_window": long_window,
                **result.summary,
            })
        leaderboard = pd.DataFrame(candidates).sort_values(["sharpe_ratio", "annualized_return"], ascending=False).reset_index(drop=True)
        leaderboard["adjusted_p_value"] = holm_bonferroni(leaderboard["p_value"].tolist())
        winner = leaderboard.iloc[0]

        live_result = run_backtest(
            test,
            execution_params,
            int(winner["short_window"]),
            int(winner["long_window"]),
            volatility_lookback,
            target_gross_leverage,
            initial_capital,
        )
        fold_results.append({
            "train_start": str(train_start.date()),
            "train_end": str(train_end.date()),
            "test_start": str(test_start.date()),
            "test_end": str(test_end.date()),
            "short_window": int(winner["short_window"]),
            "long_window": int(winner["long_window"]),
            "train_sharpe": float(winner["sharpe_ratio"]),
            "train_adjusted_p_value": float(winner["adjusted_p_value"]),
            "test_sharpe": float(live_result.summary["sharpe_ratio"]),
            "test_cost_dollars": float(live_result.summary["transaction_cost_dollars"]),
        })
        stitched_returns.append(live_result.portfolio_returns)
        stitched_trades.append(live_result.trade_log)

    stitched_portfolio_returns = pd.concat(stitched_returns).sort_index()
    stitched_trade_log = pd.concat(stitched_trades).sort_values(["date", "ticker"]).reset_index(drop=True)
    stitched_equity = (1.0 + stitched_portfolio_returns).cumprod() * initial_capital
    stitched_summary = {
        "annualized_return": float((stitched_equity.iloc[-1] / initial_capital) ** (252 / max(len(stitched_equity), 1)) - 1.0),
        "annualized_volatility": float(stitched_portfolio_returns.std(ddof=1) * (252 ** 0.5)) if len(stitched_portfolio_returns) > 1 else 0.0,
        "sharpe_ratio": float(stitched_portfolio_returns.mean() / stitched_portfolio_returns.std(ddof=1) * (252 ** 0.5)) if stitched_portfolio_returns.std(ddof=1) else 0.0,
        "max_drawdown": float((stitched_equity / stitched_equity.cummax() - 1.0).min()),
        "turnover_dollars": float((stitched_trade_log["shares"].abs() * stitched_trade_log["close"]).sum()),
        "transaction_cost_dollars": float(stitched_trade_log["transaction_cost"].sum()),
        "t_stat": 0.0,
        "p_value": 1.0,
    }
    final_result = BacktestResult(
        portfolio_returns=stitched_portfolio_returns,
        equity_curve=stitched_equity,
        trade_log=stitched_trade_log,
        summary=stitched_summary,
    )
    summary_table = pd.DataFrame(fold_results)
    best_params = {
        "short_window": int(summary_table["short_window"].mode().iloc[0]),
        "long_window": int(summary_table["long_window"].mode().iloc[0]),
    }
    return WalkForwardOutput(
        fold_results=fold_results,
        leaderboard=summary_table,
        best_params=best_params,
        stitched_result=final_result,
    )
