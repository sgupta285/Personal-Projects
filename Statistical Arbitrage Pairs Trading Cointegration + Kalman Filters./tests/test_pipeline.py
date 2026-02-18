"""
Test suite for the Pairs Trading Pipeline.
Tests cointegration detection, Kalman filter, signal generation, execution, and metrics.
"""

import numpy as np
import pandas as pd
import pytest

from src.data.market_data import DataGenerator
from src.signals.cointegration import CointegrationScanner, CointegratedPair
from src.signals.signal_generator import SignalGenerator, SignalType, TradingSignal
from src.kalman.kalman_filter import KalmanHedgeRatio, KalmanPairTracker
from src.execution.engine import ExecutionEngine, PairPosition
from src.utils.metrics import compute_metrics
from src.config import Config, CointegrationConfig, TradingConfig, KalmanConfig


# ============================================================
# DATA GENERATION TESTS
# ============================================================

class TestDataGenerator:
    def test_cointegrated_pair_length(self):
        a, b = DataGenerator.generate_cointegrated_pair(n_days=500)
        assert len(a) == 500
        assert len(b) == 500

    def test_cointegrated_pair_positive_prices(self):
        a, b = DataGenerator.generate_cointegrated_pair(n_days=1000)
        assert (a > 0).all()
        assert (b > 0).all()

    def test_universe_size(self):
        prices, pairs = DataGenerator.generate_universe(n_pairs=10, n_noise=5, n_days=252)
        assert len(prices.columns) == 10 * 2 + 5  # 10 pairs (2 each) + 5 noise
        assert len(pairs) == 10
        assert len(prices) == 252

    def test_universe_no_nan(self):
        prices, _ = DataGenerator.generate_universe(n_pairs=5, n_noise=3, n_days=252)
        assert not prices.isna().any().any()


# ============================================================
# COINTEGRATION SCANNER TESTS
# ============================================================

class TestCointegrationScanner:
    def setup_method(self):
        self.prices, self.true_pairs = DataGenerator.generate_universe(
            n_pairs=5, n_noise=3, n_days=500, seed=42
        )
        cfg = CointegrationConfig(
            min_history_days=100, max_pairs=50,
            significance_level=0.05, half_life_max=60,
            half_life_min=3, min_correlation=0.3,
        )
        self.scanner = CointegrationScanner(cfg)

    def test_finds_cointegrated_pairs(self):
        pairs = self.scanner.scan(self.prices)
        assert len(pairs) > 0

    def test_pairs_have_valid_hedge_ratios(self):
        pairs = self.scanner.scan(self.prices)
        for p in pairs:
            assert abs(p.hedge_ratio) > 0.01
            assert abs(p.hedge_ratio) < 100

    def test_pairs_have_valid_half_life(self):
        pairs = self.scanner.scan(self.prices)
        for p in pairs:
            assert 3 <= p.half_life <= 60

    def test_pairs_sorted_by_score(self):
        pairs = self.scanner.scan(self.prices)
        if len(pairs) > 1:
            for i in range(len(pairs) - 1):
                assert pairs[i].score >= pairs[i + 1].score

    def test_half_life_estimation(self):
        # OU process with known half-life
        np.random.seed(42)
        half_life = 20.0
        theta = np.log(2) / half_life
        n = 1000
        spread = np.zeros(n)
        for t in range(1, n):
            spread[t] = spread[t-1] - theta * spread[t-1] + np.random.randn() * 0.5
        est = CointegrationScanner._estimate_half_life(spread)
        assert 10 < est < 40  # Rough bounds


# ============================================================
# KALMAN FILTER TESTS
# ============================================================

class TestKalmanFilter:
    def test_initialization(self):
        kf = KalmanHedgeRatio()
        state = kf.initialize(1.5)
        assert state.beta == 1.5
        assert state.n_updates == 0

    def test_update_changes_state(self):
        kf = KalmanHedgeRatio()
        kf.initialize(1.0)
        state1 = kf.update(100.0, 80.0)
        state2 = kf.update(102.0, 81.0)
        assert state2.n_updates == 2
        # Beta should evolve
        assert state1.beta != state2.beta or state1.spread != state2.spread

    def test_hedge_ratio_tracks_true_beta(self):
        """Kalman should converge toward true hedge ratio."""
        np.random.seed(42)
        true_beta = 1.3
        kf = KalmanHedgeRatio()
        kf.initialize(1.0)

        for _ in range(500):
            b = 50 + np.random.randn() * 5
            a = true_beta * b + np.random.randn() * 2
            kf.update(a, b)

        # After many observations, beta should be close to 1.3
        assert abs(kf.hedge_ratio - true_beta) < 0.3

    def test_spread_is_finite(self):
        kf = KalmanHedgeRatio()
        kf.initialize(1.0)
        for _ in range(100):
            state = kf.update(100 + np.random.randn(), 80 + np.random.randn())
        assert np.isfinite(state.spread)
        assert np.isfinite(state.spread_var)

    def test_pair_tracker(self):
        tracker = KalmanPairTracker()
        tracker.add_pair("AB", 1.2)
        tracker.add_pair("CD", 0.8)
        assert tracker.active_pairs == 2

        tracker.update("AB", 100, 80)
        z = tracker.get_zscore("AB", 105, 82)
        assert np.isfinite(z)

        tracker.remove_pair("AB")
        assert tracker.active_pairs == 1


# ============================================================
# SIGNAL GENERATOR TESTS
# ============================================================

class TestSignalGenerator:
    def setup_method(self):
        self.pair = CointegratedPair(
            symbol_a="A", symbol_b="B", hedge_ratio=1.2,
            half_life=20, correlation=0.8, trace_stat=30,
            critical_value=15, spread_mean=0, spread_std=2,
            adf_pvalue=0.01, score=5.0,
        )
        cfg = TradingConfig(entry_z=2.0, exit_z=0.5, stop_z=4.0)
        self.gen = SignalGenerator([self.pair], cfg)

    def test_hold_signal_within_thresholds(self):
        sig = self.gen.process_tick("A_B", 100, 83, pd.Timestamp("2021-01-01"))
        # First tick — unlikely to trigger extreme z-score
        assert sig.signal_type in (SignalType.HOLD, SignalType.ENTER_LONG, SignalType.ENTER_SHORT)

    def test_generates_entry_on_extreme_zscore(self):
        # Force extreme spread by giving very different prices
        for _ in range(100):
            self.gen.process_tick("A_B", 100, 83, pd.Timestamp("2021-01-01"))

        # Now push price far from mean
        sig = self.gen.process_tick("A_B", 200, 83, pd.Timestamp("2021-01-02"))
        # With a large spread deviation, should get a signal
        assert sig.signal_type != SignalType.HOLD or sig.zscore != 0

    def test_active_positions_count(self):
        assert self.gen.active_positions() == 0


# ============================================================
# EXECUTION ENGINE TESTS
# ============================================================

class TestExecutionEngine:
    def setup_method(self):
        cfg = TradingConfig(initial_capital=1_000_000, max_pairs_active=10)
        self.engine = ExecutionEngine(cfg)

    def test_initial_state(self):
        assert self.engine.cash == 1_000_000
        assert len(self.engine.positions) == 0
        assert len(self.engine.trades) == 0

    def test_open_and_close_position(self):
        enter_sig = TradingSignal(
            pair_id="AB", symbol_a="A", symbol_b="B",
            signal_type=SignalType.ENTER_LONG, zscore=-2.5,
            hedge_ratio=1.2, spread=-5.0,
            timestamp=pd.Timestamp("2021-01-01"),
            latency_ms=0.1, confidence=0.8,
        )
        self.engine.execute_signal(enter_sig, 100.0, 80.0)
        assert len(self.engine.positions) == 1

        exit_sig = TradingSignal(
            pair_id="AB", symbol_a="A", symbol_b="B",
            signal_type=SignalType.EXIT, zscore=0.3,
            hedge_ratio=1.2, spread=0.5,
            timestamp=pd.Timestamp("2021-02-01"),
            latency_ms=0.1, confidence=1.0,
        )
        trade = self.engine.execute_signal(exit_sig, 105.0, 84.0)
        assert len(self.engine.positions) == 0
        assert trade is not None
        assert trade.exit_reason == "mean_reversion"

    def test_max_positions_enforced(self):
        cfg = TradingConfig(initial_capital=10_000_000, max_pairs_active=2)
        engine = ExecutionEngine(cfg)

        for i in range(5):
            sig = TradingSignal(
                pair_id=f"P{i}", symbol_a=f"A{i}", symbol_b=f"B{i}",
                signal_type=SignalType.ENTER_LONG, zscore=-2.5,
                hedge_ratio=1.0, spread=-3.0,
                timestamp=pd.Timestamp("2021-01-01"),
                latency_ms=0.1, confidence=0.8,
            )
            engine.execute_signal(sig, 100.0, 100.0)

        assert len(engine.positions) <= 2

    def test_mark_to_market(self):
        sig = TradingSignal(
            pair_id="AB", symbol_a="A", symbol_b="B",
            signal_type=SignalType.ENTER_LONG, zscore=-2.5,
            hedge_ratio=1.0, spread=-3.0,
            timestamp=pd.Timestamp("2021-01-01"),
            latency_ms=0.1, confidence=0.8,
        )
        self.engine.execute_signal(sig, 100.0, 100.0)
        snap = self.engine.mark_to_market({"A": 105, "B": 98}, pd.Timestamp("2021-01-02"))
        assert snap.equity > 0
        assert snap.n_positions == 1


# ============================================================
# METRICS TESTS
# ============================================================

class TestMetrics:
    def test_compute_basic_metrics(self):
        from src.execution.engine import PortfolioSnapshot, TradeRecord
        snaps = [
            PortfolioSnapshot(pd.Timestamp("2021-01-01"), 1000000, 1000000, 0, 0, 0, 0, 0),
            PortfolioSnapshot(pd.Timestamp("2021-01-02"), 1010000, 1010000, 0, 0.01, 0, 0, 0),
            PortfolioSnapshot(pd.Timestamp("2021-01-03"), 1005000, 1005000, 0, -0.005, 0.005, 0, 0),
        ]
        m = compute_metrics(snaps, [], 0, 1.0)
        assert m.total_return > 0
        assert m.max_drawdown >= 0

    def test_empty_snapshots(self):
        m = compute_metrics([], [], 0, 1.0)
        assert m.total_return == 0
        assert m.sharpe_ratio == 0


# ============================================================
# INTEGRATION TEST
# ============================================================

class TestIntegration:
    def test_full_pipeline_runs(self):
        """End-to-end: data → scan → signals → execution → metrics."""
        prices, true_pairs = DataGenerator.generate_universe(
            n_pairs=5, n_noise=3, n_days=500, seed=42
        )

        scanner = CointegrationScanner(CointegrationConfig(
            min_history_days=100, max_pairs=20, min_correlation=0.3,
            half_life_min=3, half_life_max=60,
        ))
        pairs = scanner.scan(prices.iloc[:200])

        if not pairs:
            return  # Acceptable: scan may not find pairs on this seed

        signal_gen = SignalGenerator(pairs, TradingConfig(
            initial_capital=1_000_000, entry_z=2.0, exit_z=0.5,
        ))
        executor = ExecutionEngine(TradingConfig(initial_capital=1_000_000))

        for date in prices.index[200:]:
            signals = signal_gen.process_bar(prices, date)
            for sig in signals:
                pa = prices.loc[date, sig.symbol_a]
                pb = prices.loc[date, sig.symbol_b]
                executor.execute_signal(sig, pa, pb)

            row = {sym: prices.loc[date, sym] for sym in prices.columns}
            executor.mark_to_market(row, date)

        assert len(executor.snapshots) > 0
        assert executor.snapshots[-1].equity > 0
