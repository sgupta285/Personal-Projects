"""
Market data generation and management.
Generates synthetic cointegrated pairs for testing, or loads from CSV/database.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()


@dataclass
class TickData:
    symbol: str
    timestamp: pd.Timestamp
    price: float
    volume: float


class DataGenerator:
    """Generate synthetic cointegrated price series for testing."""

    @staticmethod
    def generate_cointegrated_pair(
        n_days: int = 756,
        spread_mean: float = 0.0,
        spread_std: float = 1.0,
        half_life: float = 20.0,
        beta: float = 1.2,
        base_price_a: float = 100.0,
        base_price_b: float = 120.0,
        noise_std: float = 0.5,
        seed: int = 42,
    ) -> Tuple[pd.Series, pd.Series]:
        """Generate a pair of cointegrated price series using OU process for spread."""
        np.random.seed(seed)

        # Generate mean-reverting spread (Ornstein-Uhlenbeck)
        theta = np.log(2) / half_life  # Mean-reversion speed
        dt = 1.0
        spread = np.zeros(n_days)
        spread[0] = spread_mean

        for t in range(1, n_days):
            dW = np.random.randn() * spread_std * np.sqrt(dt)
            spread[t] = spread[t - 1] + theta * (spread_mean - spread[t - 1]) * dt + dW

        # Generate asset A with random walk + drift
        log_returns_a = np.random.randn(n_days) * 0.015 + 0.0002
        prices_a = base_price_a * np.exp(np.cumsum(log_returns_a))

        # Generate asset B = beta * A + spread + noise
        prices_b = beta * prices_a + spread + np.random.randn(n_days) * noise_std
        prices_b = np.maximum(prices_b, 1.0)  # Floor at $1
        # Shift to target base price
        prices_b = prices_b * (base_price_b / prices_b[0])

        dates = pd.bdate_range(start="2020-01-02", periods=n_days)
        return (
            pd.Series(prices_a, index=dates, name="STOCK_A"),
            pd.Series(prices_b, index=dates, name="STOCK_B"),
        )

    @staticmethod
    def generate_universe(
        n_pairs: int = 30,
        n_noise: int = 20,
        n_days: int = 756,
        seed: int = 42,
    ) -> pd.DataFrame:
        """
        Generate a stock universe with n_pairs cointegrated pairs + n_noise random stocks.
        Returns DataFrame with columns as symbols, index as dates.
        """
        np.random.seed(seed)
        all_prices = {}
        pair_registry = []

        for i in range(n_pairs):
            sym_a = f"CI_A{i:02d}"
            sym_b = f"CI_B{i:02d}"

            half_life = np.random.uniform(8, 45)
            beta = np.random.uniform(0.6, 1.8)
            base_a = np.random.uniform(30, 300)
            base_b = np.random.uniform(30, 300)

            a, b = DataGenerator.generate_cointegrated_pair(
                n_days=n_days,
                half_life=half_life,
                beta=beta,
                base_price_a=base_a,
                base_price_b=base_b,
                seed=seed + i * 100,
            )

            all_prices[sym_a] = a.values
            all_prices[sym_b] = b.values
            pair_registry.append((sym_a, sym_b, beta, half_life))

        # Random walk noise stocks (not cointegrated with anything)
        for i in range(n_noise):
            sym = f"RW_{i:02d}"
            base = np.random.uniform(20, 400)
            returns = np.random.randn(n_days) * 0.02 + 0.0001
            prices = base * np.exp(np.cumsum(returns))
            all_prices[sym] = prices

        dates = pd.bdate_range(start="2020-01-02", periods=n_days)
        df = pd.DataFrame(all_prices, index=dates)

        logger.info(
            "universe_generated",
            n_pairs=n_pairs,
            n_noise=n_noise,
            total_symbols=len(df.columns),
            n_days=n_days,
        )

        return df, pair_registry

    @staticmethod
    def simulate_tick_stream(
        prices: pd.DataFrame, ticks_per_bar: int = 100
    ) -> List[TickData]:
        """Convert daily bars to simulated tick stream for latency testing."""
        ticks = []
        for date in prices.index:
            for sym in prices.columns:
                price = prices.loc[date, sym]
                base_time = pd.Timestamp(date)
                for t in range(ticks_per_bar):
                    # Add intraday noise
                    noise = np.random.randn() * price * 0.001
                    tick_time = base_time + pd.Timedelta(seconds=t * (6.5 * 3600 / ticks_per_bar))
                    ticks.append(
                        TickData(sym, tick_time, price + noise, np.random.uniform(100, 10000))
                    )
        return ticks
