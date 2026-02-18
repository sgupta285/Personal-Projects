"""
Execution Engine: manages positions, tracks P&L, enforces risk limits.
Simulates realistic execution with slippage and commissions.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import structlog

from src.config import config
from src.signals.signal_generator import TradingSignal, SignalType

logger = structlog.get_logger()


@dataclass
class PairPosition:
    pair_id: str
    symbol_a: str
    symbol_b: str
    qty_a: int = 0
    qty_b: int = 0
    entry_price_a: float = 0.0
    entry_price_b: float = 0.0
    hedge_ratio: float = 1.0
    entry_spread: float = 0.0
    entry_zscore: float = 0.0
    entry_time: Optional[pd.Timestamp] = None
    direction: str = ""  # "long_spread" or "short_spread"
    unrealized_pnl: float = 0.0


@dataclass
class TradeRecord:
    pair_id: str
    symbol_a: str
    symbol_b: str
    direction: str
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    entry_spread: float
    exit_spread: float
    entry_zscore: float
    exit_zscore: float
    pnl: float
    return_pct: float
    holding_days: int
    exit_reason: str  # "mean_reversion", "stop_loss"


@dataclass
class PortfolioSnapshot:
    timestamp: pd.Timestamp
    equity: float
    cash: float
    positions_value: float
    daily_return: float
    drawdown: float
    n_positions: int
    n_trades_today: int


class ExecutionEngine:
    """Manages order execution, position tracking, and portfolio state."""

    def __init__(self, cfg=None):
        self.cfg = cfg or config.trading
        self.cash = self.cfg.initial_capital
        self.initial_capital = self.cfg.initial_capital
        self.positions: Dict[str, PairPosition] = {}
        self.trades: List[TradeRecord] = []
        self.snapshots: List[PortfolioSnapshot] = []
        self._peak_equity = self.cfg.initial_capital
        self._prev_equity = self.cfg.initial_capital

    def execute_signal(
        self, signal: TradingSignal, price_a: float, price_b: float
    ) -> Optional[TradeRecord]:
        """Execute a trading signal. Returns TradeRecord if a position was closed."""
        if signal.signal_type == SignalType.HOLD:
            return None

        if signal.signal_type in (SignalType.ENTER_LONG, SignalType.ENTER_SHORT):
            return self._open_position(signal, price_a, price_b)
        elif signal.signal_type in (SignalType.EXIT, SignalType.STOP_LOSS):
            return self._close_position(signal, price_a, price_b)

        return None

    def _open_position(
        self, signal: TradingSignal, price_a: float, price_b: float
    ) -> None:
        """Open a new pairs position."""
        if signal.pair_id in self.positions:
            return None  # Already have position
        if len(self.positions) >= self.cfg.max_pairs_active:
            return None  # At capacity

        equity = self._current_equity({})
        notional = equity * self.cfg.max_position_pct
        hedge = abs(signal.hedge_ratio)

        # Size: equal dollar exposure on each leg
        qty_a = int(notional / (2 * price_a))
        qty_b = int(notional / (2 * price_b * hedge)) if hedge > 0 else 0

        if qty_a <= 0 or qty_b <= 0:
            return None

        # Apply slippage
        slip_a = price_a * self.cfg.slippage_bps / 10000
        slip_b = price_b * self.cfg.slippage_bps / 10000
        comm_a = price_a * qty_a * self.cfg.commission_bps / 10000
        comm_b = price_b * qty_b * self.cfg.commission_bps / 10000

        direction = "long_spread" if signal.signal_type == SignalType.ENTER_LONG else "short_spread"

        if direction == "long_spread":
            # Buy A, Sell B
            cost = (price_a + slip_a) * qty_a - (price_b - slip_b) * qty_b + comm_a + comm_b
            pos = PairPosition(
                pair_id=signal.pair_id, symbol_a=signal.symbol_a, symbol_b=signal.symbol_b,
                qty_a=qty_a, qty_b=-qty_b,
                entry_price_a=price_a + slip_a, entry_price_b=price_b - slip_b,
                hedge_ratio=signal.hedge_ratio, entry_spread=signal.spread,
                entry_zscore=signal.zscore, entry_time=signal.timestamp, direction=direction,
            )
        else:
            # Sell A, Buy B
            cost = -(price_a - slip_a) * qty_a + (price_b + slip_b) * qty_b + comm_a + comm_b
            pos = PairPosition(
                pair_id=signal.pair_id, symbol_a=signal.symbol_a, symbol_b=signal.symbol_b,
                qty_a=-qty_a, qty_b=qty_b,
                entry_price_a=price_a - slip_a, entry_price_b=price_b + slip_b,
                hedge_ratio=signal.hedge_ratio, entry_spread=signal.spread,
                entry_zscore=signal.zscore, entry_time=signal.timestamp, direction=direction,
            )

        self.cash -= cost
        self.positions[signal.pair_id] = pos
        logger.info("position_opened", pair=signal.pair_id, direction=direction,
                     z=f"{signal.zscore:.2f}", qty_a=pos.qty_a, qty_b=pos.qty_b)
        return None

    def _close_position(
        self, signal: TradingSignal, price_a: float, price_b: float
    ) -> Optional[TradeRecord]:
        """Close an existing pairs position."""
        pos = self.positions.pop(signal.pair_id, None)
        if pos is None:
            return None

        slip_a = price_a * self.cfg.slippage_bps / 10000
        slip_b = price_b * self.cfg.slippage_bps / 10000
        comm = (abs(pos.qty_a) * price_a + abs(pos.qty_b) * price_b) * self.cfg.commission_bps / 10000

        # P&L from closing
        if pos.qty_a > 0:
            pnl_a = pos.qty_a * ((price_a - slip_a) - pos.entry_price_a)
        else:
            pnl_a = abs(pos.qty_a) * (pos.entry_price_a - (price_a + slip_a))

        if pos.qty_b > 0:
            pnl_b = pos.qty_b * ((price_b - slip_b) - pos.entry_price_b)
        else:
            pnl_b = abs(pos.qty_b) * (pos.entry_price_b - (price_b + slip_b))

        total_pnl = pnl_a + pnl_b - comm
        self.cash += total_pnl

        # Also return capital from closed positions
        notional_closed = abs(pos.qty_a) * price_a + abs(pos.qty_b) * price_b
        self.cash += notional_closed / 2  # Approximate

        entry_notional = abs(pos.qty_a) * pos.entry_price_a + abs(pos.qty_b) * pos.entry_price_b
        return_pct = total_pnl / (entry_notional + 1e-10)

        holding = (signal.timestamp - pos.entry_time).days if pos.entry_time else 0
        exit_reason = "stop_loss" if signal.signal_type == SignalType.STOP_LOSS else "mean_reversion"

        trade = TradeRecord(
            pair_id=pos.pair_id, symbol_a=pos.symbol_a, symbol_b=pos.symbol_b,
            direction=pos.direction, entry_time=pos.entry_time, exit_time=signal.timestamp,
            entry_spread=pos.entry_spread, exit_spread=signal.spread,
            entry_zscore=pos.entry_zscore, exit_zscore=signal.zscore,
            pnl=total_pnl, return_pct=return_pct, holding_days=holding, exit_reason=exit_reason,
        )
        self.trades.append(trade)
        logger.info("position_closed", pair=pos.pair_id, pnl=f"${total_pnl:,.0f}",
                     exit=exit_reason, holding=f"{holding}d")
        return trade

    def mark_to_market(
        self, prices: Dict[str, float], timestamp: pd.Timestamp
    ) -> PortfolioSnapshot:
        """Mark all positions and record portfolio snapshot."""
        pos_value = 0.0
        for pos in self.positions.values():
            pa = prices.get(pos.symbol_a, pos.entry_price_a)
            pb = prices.get(pos.symbol_b, pos.entry_price_b)
            pos.unrealized_pnl = (
                pos.qty_a * (pa - pos.entry_price_a) + pos.qty_b * (pb - pos.entry_price_b)
            )
            pos_value += pos.unrealized_pnl

        equity = self.cash + pos_value
        daily_ret = (equity / self._prev_equity - 1) if self._prev_equity > 0 else 0
        self._peak_equity = max(self._peak_equity, equity)
        dd = 1 - equity / self._peak_equity if self._peak_equity > 0 else 0

        snap = PortfolioSnapshot(
            timestamp=timestamp, equity=equity, cash=self.cash, positions_value=pos_value,
            daily_return=daily_ret, drawdown=dd, n_positions=len(self.positions), n_trades_today=0,
        )
        self.snapshots.append(snap)
        self._prev_equity = equity
        return snap

    def _current_equity(self, prices: Dict[str, float]) -> float:
        return self.cash + sum(
            p.unrealized_pnl for p in self.positions.values()
        )

    @property
    def equity(self) -> float:
        return self.snapshots[-1].equity if self.snapshots else self.initial_capital

    @property
    def total_pnl(self) -> float:
        return sum(t.pnl for t in self.trades)
