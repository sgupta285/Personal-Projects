"""
Signal Generator: produces trading signals from z-score crossings.

Signal logic:
  ENTER LONG spread:  z < -entry_z  → Buy A, Sell β*B
  ENTER SHORT spread: z > +entry_z  → Sell A, Buy β*B
  EXIT:               |z| < exit_z  → Close position
  STOP:               |z| > stop_z  → Emergency close
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict
import time
import structlog

from src.config import config
from src.signals.cointegration import CointegratedPair
from src.kalman.kalman_filter import KalmanPairTracker

logger = structlog.get_logger()


class SignalType(Enum):
    ENTER_LONG = "enter_long"    # Spread undervalued: buy A, sell B
    ENTER_SHORT = "enter_short"  # Spread overvalued: sell A, buy B
    EXIT = "exit"                # Mean reverted: close
    STOP_LOSS = "stop_loss"      # Spread diverging: emergency close
    HOLD = "hold"                # No action


@dataclass
class TradingSignal:
    pair_id: str
    symbol_a: str
    symbol_b: str
    signal_type: SignalType
    zscore: float
    hedge_ratio: float
    spread: float
    timestamp: pd.Timestamp
    latency_ms: float
    confidence: float  # 0-1 signal strength


class SignalGenerator:
    """
    Generates trading signals for cointegrated pairs using Kalman-filtered
    hedge ratios and z-score thresholds.
    """

    def __init__(self, pairs: List[CointegratedPair], cfg=None):
        self.cfg = cfg or config.trading
        self.pairs = {f"{p.symbol_a}_{p.symbol_b}": p for p in pairs}
        self.kalman = KalmanPairTracker()
        self._positions: Dict[str, SignalType] = {}  # pair_id -> current position

        # Initialize Kalman filters with cointegration hedge ratios
        for pair_id, pair in self.pairs.items():
            self.kalman.add_pair(pair_id, pair.hedge_ratio)

    def process_tick(
        self, pair_id: str, price_a: float, price_b: float, timestamp: pd.Timestamp
    ) -> TradingSignal:
        """
        Process a price update and generate signal.

        Returns:
            TradingSignal with action and metadata
        """
        t0 = time.perf_counter()

        pair = self.pairs.get(pair_id)
        if pair is None:
            return self._no_signal(pair_id, timestamp, 0.0)

        # Update Kalman filter
        state = self.kalman.update(pair_id, price_a, price_b)
        z = self.kalman.get_zscore(pair_id, price_a, price_b)
        hedge = self.kalman.get_hedge_ratio(pair_id)
        spread = state.spread

        current_pos = self._positions.get(pair_id)

        # Determine signal
        signal_type = SignalType.HOLD
        confidence = 0.0

        if current_pos in (SignalType.ENTER_LONG, SignalType.ENTER_SHORT):
            # Already in position — check for exit or stop
            if abs(z) > self.cfg.stop_z:
                signal_type = SignalType.STOP_LOSS
                confidence = 1.0
            elif abs(z) < self.cfg.exit_z:
                signal_type = SignalType.EXIT
                confidence = 1.0 - abs(z) / self.cfg.exit_z
        else:
            # Not in position — check for entry
            if z < -self.cfg.entry_z:
                signal_type = SignalType.ENTER_LONG
                confidence = min(abs(z) / self.cfg.stop_z, 1.0)
            elif z > self.cfg.entry_z:
                signal_type = SignalType.ENTER_SHORT
                confidence = min(abs(z) / self.cfg.stop_z, 1.0)

        # Update position tracker
        if signal_type in (SignalType.ENTER_LONG, SignalType.ENTER_SHORT):
            self._positions[pair_id] = signal_type
        elif signal_type in (SignalType.EXIT, SignalType.STOP_LOSS):
            self._positions.pop(pair_id, None)

        latency_ms = (time.perf_counter() - t0) * 1000

        return TradingSignal(
            pair_id=pair_id,
            symbol_a=pair.symbol_a,
            symbol_b=pair.symbol_b,
            signal_type=signal_type,
            zscore=float(z),
            hedge_ratio=float(hedge),
            spread=float(spread),
            timestamp=timestamp,
            latency_ms=latency_ms,
            confidence=confidence,
        )

    def process_bar(
        self, prices: pd.DataFrame, date: pd.Timestamp
    ) -> List[TradingSignal]:
        """Process daily bar for all pairs. Returns list of non-HOLD signals."""
        signals = []
        for pair_id, pair in self.pairs.items():
            if pair.symbol_a in prices.columns and pair.symbol_b in prices.columns:
                price_a = prices.loc[date, pair.symbol_a]
                price_b = prices.loc[date, pair.symbol_b]
                signal = self.process_tick(pair_id, price_a, price_b, date)
                if signal.signal_type != SignalType.HOLD:
                    signals.append(signal)
        return signals

    def active_positions(self) -> int:
        return len(self._positions)

    def _no_signal(self, pair_id, ts, latency):
        return TradingSignal(pair_id, "", "", SignalType.HOLD, 0, 0, 0, ts, latency, 0)
