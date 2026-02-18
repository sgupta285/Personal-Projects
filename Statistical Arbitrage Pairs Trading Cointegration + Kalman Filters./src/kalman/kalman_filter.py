"""
Kalman Filter for dynamic hedge ratio estimation.
Tracks time-varying beta (hedge ratio) between cointegrated pairs
under changing market regimes.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Tuple
import structlog

from src.config import config

logger = structlog.get_logger()


@dataclass
class KalmanState:
    """State of the Kalman filter at time t."""
    beta: float              # Current hedge ratio estimate
    intercept: float         # Current intercept estimate
    P: np.ndarray            # 2x2 state covariance matrix
    R: float                 # Observation noise variance (estimated)
    Q: np.ndarray            # 2x2 process noise covariance
    spread: float = 0.0      # Current spread residual
    spread_var: float = 1.0  # Spread variance
    n_updates: int = 0


class KalmanHedgeRatio:
    """
    Online Kalman filter for estimating dynamic hedge ratios.

    State: [intercept, beta]
    Observation: price_a = intercept + beta * price_b + noise

    The filter adapts the hedge ratio over time, capturing regime changes
    that a static OLS regression would miss.
    """

    def __init__(self, cfg=None):
        self.cfg = cfg or config.kalman
        self._state = None

    def initialize(self, initial_beta: float = 1.0) -> KalmanState:
        """Initialize filter with prior estimate of hedge ratio."""
        P = np.eye(2) * self.cfg.initial_state_cov
        Q = np.eye(2) * self.cfg.delta
        self._state = KalmanState(
            beta=initial_beta,
            intercept=0.0,
            P=P,
            R=self.cfg.observation_noise,
            Q=Q,
        )
        return self._state

    def update(self, price_a: float, price_b: float) -> KalmanState:
        """
        Process one observation and update hedge ratio estimate.

        Args:
            price_a: Price of asset A (dependent variable)
            price_b: Price of asset B (independent variable)

        Returns:
            Updated KalmanState with new beta, spread, and covariance
        """
        if self._state is None:
            self.initialize()

        state = self._state

        # State vector: x = [intercept, beta]
        x = np.array([state.intercept, state.beta])

        # Observation matrix: H = [1, price_b]
        H = np.array([1.0, price_b])

        # Prediction step
        # x_pred = x (random walk state transition: F = I)
        P_pred = state.P + state.Q

        # Innovation (measurement residual)
        y_pred = H @ x  # predicted price_a
        innovation = price_a - y_pred

        # Innovation covariance
        S = H @ P_pred @ H.T + state.R

        # Kalman gain
        K = P_pred @ H.T / S

        # Update step
        x_new = x + K * innovation
        P_new = (np.eye(2) - np.outer(K, H)) @ P_pred

        # Update observation noise estimate (adaptive R)
        state.R = max(0.5 * state.R + 0.5 * innovation ** 2, 1e-6)

        # Store state
        state.intercept = float(x_new[0])
        state.beta = float(x_new[1])
        state.P = P_new
        state.spread = float(innovation)
        state.spread_var = float(S)
        state.n_updates += 1

        return state

    def get_spread(self, price_a: float, price_b: float) -> float:
        """Compute spread using current Kalman hedge ratio."""
        if self._state is None:
            return 0.0
        return price_a - self._state.intercept - self._state.beta * price_b

    def get_zscore(self, price_a: float, price_b: float) -> float:
        """Compute z-score of spread using Kalman-estimated variance."""
        if self._state is None or self._state.spread_var <= 0:
            return 0.0
        spread = self.get_spread(price_a, price_b)
        return spread / np.sqrt(self._state.spread_var)

    @property
    def state(self) -> KalmanState:
        return self._state

    @property
    def hedge_ratio(self) -> float:
        return self._state.beta if self._state else 1.0

    def reset(self):
        """Reset filter state."""
        self._state = None


class KalmanPairTracker:
    """Manages Kalman filters for multiple pairs simultaneously."""

    def __init__(self, cfg=None):
        self.cfg = cfg or config.kalman
        self._filters = {}

    def add_pair(self, pair_id: str, initial_beta: float = 1.0):
        """Initialize a Kalman filter for a new pair."""
        kf = KalmanHedgeRatio(self.cfg)
        kf.initialize(initial_beta)
        self._filters[pair_id] = kf

    def update(self, pair_id: str, price_a: float, price_b: float) -> KalmanState:
        """Update the filter for a specific pair."""
        if pair_id not in self._filters:
            self.add_pair(pair_id)
        return self._filters[pair_id].update(price_a, price_b)

    def get_zscore(self, pair_id: str, price_a: float, price_b: float) -> float:
        """Get current z-score for a pair."""
        if pair_id not in self._filters:
            return 0.0
        return self._filters[pair_id].get_zscore(price_a, price_b)

    def get_hedge_ratio(self, pair_id: str) -> float:
        """Get current hedge ratio for a pair."""
        if pair_id not in self._filters:
            return 1.0
        return self._filters[pair_id].hedge_ratio

    def remove_pair(self, pair_id: str):
        self._filters.pop(pair_id, None)

    @property
    def active_pairs(self) -> int:
        return len(self._filters)
