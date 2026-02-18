"""
Cointegration Scanner: identifies pairs via Johansen test with pre-filtering.

Pipeline:
1. Correlation pre-filter (min_correlation) to reduce O(n²) Johansen tests
2. Johansen cointegration test at specified significance level
3. Half-life filter (Ornstein-Uhlenbeck estimation)
4. Rank pairs by cointegration strength and return top N
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional
from dataclasses import dataclass
from itertools import combinations
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant
import structlog

from src.config import config

logger = structlog.get_logger()


@dataclass
class CointegratedPair:
    symbol_a: str
    symbol_b: str
    hedge_ratio: float       # β: units of B per unit of A
    half_life: float         # Mean-reversion half-life in days
    correlation: float       # Pearson correlation
    trace_stat: float        # Johansen trace statistic
    critical_value: float    # 5% critical value
    spread_mean: float
    spread_std: float
    adf_pvalue: float        # ADF test on spread
    score: float             # Composite ranking score


class CointegrationScanner:
    def __init__(self, cfg=None):
        self.cfg = cfg or config.coint

    def scan(self, prices: pd.DataFrame) -> List[CointegratedPair]:
        """
        Full cointegration scan across all symbol pairs.

        Args:
            prices: DataFrame with columns as symbols, index as dates

        Returns:
            List of CointegratedPair, sorted by composite score (descending)
        """
        symbols = list(prices.columns)
        n = len(symbols)
        logger.info("scan_started", n_symbols=n, n_candidate_pairs=n * (n - 1) // 2)

        # Step 1: Correlation pre-filter
        corr_matrix = prices.pct_change().dropna().corr()
        candidate_pairs = []

        for i, j in combinations(range(n), 2):
            corr = abs(corr_matrix.iloc[i, j])
            if corr >= self.cfg.min_correlation:
                candidate_pairs.append((symbols[i], symbols[j], corr))

        logger.info("correlation_filter", candidates=len(candidate_pairs), threshold=self.cfg.min_correlation)

        # Step 2: Johansen cointegration test on each candidate
        pairs = []
        for sym_a, sym_b, corr in candidate_pairs:
            result = self._test_pair(prices[sym_a], prices[sym_b], sym_a, sym_b, corr)
            if result is not None:
                pairs.append(result)

        # Step 3: Sort by composite score and take top N
        pairs.sort(key=lambda p: p.score, reverse=True)
        pairs = pairs[: self.cfg.max_pairs]

        logger.info("scan_complete", cointegrated_pairs=len(pairs))
        return pairs

    def _test_pair(
        self, series_a: pd.Series, series_b: pd.Series,
        sym_a: str, sym_b: str, correlation: float
    ) -> Optional[CointegratedPair]:
        """Run Johansen cointegration test on a pair."""
        try:
            data = pd.concat([series_a, series_b], axis=1).dropna()
            if len(data) < self.cfg.min_history_days:
                return None

            # Johansen test (det_order=-1 = no deterministic terms, 1 lag)
            result = coint_johansen(data.values, det_order=0, k_ar_diff=1)

            trace_stat = result.lr1[0]      # Trace statistic for r=0
            crit_value = result.cvt[0, 1]   # 5% critical value

            if trace_stat < crit_value:
                return None  # Not cointegrated

            # Extract hedge ratio from eigenvector
            eigenvec = result.evec[:, 0]
            hedge_ratio = -eigenvec[1] / eigenvec[0]

            # Compute spread
            spread = series_a.values - hedge_ratio * series_b.values

            # Estimate half-life via AR(1) on spread
            half_life = self._estimate_half_life(spread)
            if half_life < self.cfg.half_life_min or half_life > self.cfg.half_life_max:
                return None

            # ADF test on spread
            from statsmodels.tsa.stattools import adfuller
            adf_result = adfuller(spread, maxlag=1)
            adf_pvalue = adf_result[1]

            if adf_pvalue > self.cfg.significance_level:
                return None  # Spread not stationary

            spread_mean = float(np.mean(spread))
            spread_std = float(np.std(spread))

            # Composite score: higher trace stat + lower half-life + lower ADF p-value
            score = (trace_stat / crit_value) * (1.0 / half_life) * (1.0 - adf_pvalue)

            return CointegratedPair(
                symbol_a=sym_a,
                symbol_b=sym_b,
                hedge_ratio=float(hedge_ratio),
                half_life=float(half_life),
                correlation=float(correlation),
                trace_stat=float(trace_stat),
                critical_value=float(crit_value),
                spread_mean=spread_mean,
                spread_std=spread_std,
                adf_pvalue=float(adf_pvalue),
                score=float(score),
            )
        except Exception as e:
            logger.debug("pair_test_failed", sym_a=sym_a, sym_b=sym_b, error=str(e))
            return None

    @staticmethod
    def _estimate_half_life(spread: np.ndarray) -> float:
        """Estimate mean-reversion half-life via AR(1) regression on spread."""
        spread_lag = spread[:-1]
        spread_diff = np.diff(spread)

        spread_lag = add_constant(spread_lag)
        model = OLS(spread_diff, spread_lag).fit()

        theta = model.params[1]  # Mean-reversion coefficient
        if theta >= 0:
            return 999.0  # Not mean-reverting

        half_life = -np.log(2) / theta
        return float(half_life)

    @staticmethod
    def compute_spread(
        prices_a: np.ndarray, prices_b: np.ndarray, hedge_ratio: float
    ) -> np.ndarray:
        """Compute spread = A - β * B."""
        return prices_a - hedge_ratio * prices_b

    @staticmethod
    def compute_zscore(spread: np.ndarray, window: int = 60) -> np.ndarray:
        """Compute rolling z-score of spread."""
        s = pd.Series(spread)
        mean = s.rolling(window).mean()
        std = s.rolling(window).std()
        z = (s - mean) / std
        return z.values
