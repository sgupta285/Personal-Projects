"""
Performance metrics for pairs trading strategy evaluation.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List

from src.execution.engine import TradeRecord, PortfolioSnapshot


@dataclass
class StrategyMetrics:
    total_return: float
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: float
    win_rate: float
    profit_factor: float
    avg_trade_pnl: float
    avg_winner: float
    avg_loser: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_holding_days: float
    stop_loss_pct: float
    max_consecutive_losses: int
    ticks_per_sec: float


def compute_metrics(
    snapshots: List[PortfolioSnapshot],
    trades: List[TradeRecord],
    ticks_processed: int = 0,
    elapsed_sec: float = 1.0,
    risk_free_rate: float = 0.04,
) -> StrategyMetrics:
    """Compute comprehensive strategy performance metrics."""
    if len(snapshots) < 2:
        return StrategyMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    equities = np.array([s.equity for s in snapshots])
    returns = np.diff(equities) / equities[:-1]
    n = len(returns)
    years = n / 252.0

    total_ret = equities[-1] / equities[0] - 1
    ann_ret = (1 + total_ret) ** (1 / years) - 1 if years > 0 else 0
    ann_vol = np.std(returns) * np.sqrt(252) if n > 1 else 0

    daily_rf = risk_free_rate / 252
    excess = returns - daily_rf
    sharpe = (np.mean(excess) / np.std(excess) * np.sqrt(252)) if np.std(excess) > 0 else 0

    downside = returns[returns < daily_rf]
    down_dev = np.std(downside) * np.sqrt(252) if len(downside) > 1 else 0
    sortino = (ann_ret - risk_free_rate) / down_dev if down_dev > 0 else 0

    max_dd = max(s.drawdown for s in snapshots) if snapshots else 0
    calmar = ann_ret / max_dd if max_dd > 0 else 0

    # Trade metrics
    winners = [t for t in trades if t.pnl > 0]
    losers = [t for t in trades if t.pnl <= 0]
    stops = [t for t in trades if t.exit_reason == "stop_loss"]

    win_rate = len(winners) / len(trades) if trades else 0
    gross_profit = sum(t.pnl for t in winners) if winners else 0
    gross_loss = abs(sum(t.pnl for t in losers)) if losers else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else (999 if gross_profit > 0 else 0)

    avg_pnl = np.mean([t.pnl for t in trades]) if trades else 0
    avg_winner = np.mean([t.pnl for t in winners]) if winners else 0
    avg_loser = np.mean([abs(t.pnl) for t in losers]) if losers else 0
    avg_holding = np.mean([t.holding_days for t in trades]) if trades else 0

    # Max consecutive losses
    max_consec = 0
    current_streak = 0
    for t in trades:
        if t.pnl <= 0:
            current_streak += 1
            max_consec = max(max_consec, current_streak)
        else:
            current_streak = 0

    tps = ticks_processed / elapsed_sec if elapsed_sec > 0 else 0

    return StrategyMetrics(
        total_return=total_ret, annualized_return=ann_ret,
        annualized_volatility=ann_vol, sharpe_ratio=sharpe, sortino_ratio=sortino,
        max_drawdown=max_dd, calmar_ratio=calmar, win_rate=win_rate,
        profit_factor=profit_factor, avg_trade_pnl=avg_pnl,
        avg_winner=avg_winner, avg_loser=avg_loser,
        total_trades=len(trades), winning_trades=len(winners), losing_trades=len(losers),
        avg_holding_days=avg_holding,
        stop_loss_pct=len(stops) / len(trades) if trades else 0,
        max_consecutive_losses=max_consec, ticks_per_sec=tps,
    )


def print_metrics(m: StrategyMetrics):
    print(f"\n{'='*60}")
    print(f"  PAIRS TRADING STRATEGY RESULTS")
    print(f"{'='*60}")
    print(f"  Total Return:        {m.total_return*100:>8.1f}%")
    print(f"  Annualized Return:   {m.annualized_return*100:>8.1f}%")
    print(f"  Annualized Vol:      {m.annualized_volatility*100:>8.1f}%")
    print(f"  Sharpe Ratio:        {m.sharpe_ratio:>8.2f}")
    print(f"  Sortino Ratio:       {m.sortino_ratio:>8.2f}")
    print(f"  Calmar Ratio:        {m.calmar_ratio:>8.2f}")
    print(f"  Max Drawdown:        {m.max_drawdown*100:>8.1f}%")
    print(f"  Win Rate:            {m.win_rate*100:>8.1f}%")
    print(f"  Profit Factor:       {m.profit_factor:>8.2f}")
    print(f"  Avg Trade P&L:       ${m.avg_trade_pnl:>10,.0f}")
    print(f"  Avg Winner:          ${m.avg_winner:>10,.0f}")
    print(f"  Avg Loser:           ${m.avg_loser:>10,.0f}")
    print(f"  Total Trades:        {m.total_trades:>8}")
    print(f"  Avg Holding (days):  {m.avg_holding_days:>8.1f}")
    print(f"  Stop-Loss Rate:      {m.stop_loss_pct*100:>8.1f}%")
    print(f"  Max Consec Losses:   {m.max_consecutive_losses:>8}")
    print(f"  Throughput:          {m.ticks_per_sec:>8,.0f} ticks/sec")
    print(f"{'='*60}\n")
