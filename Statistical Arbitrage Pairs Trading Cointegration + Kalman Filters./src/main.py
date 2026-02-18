"""
Main Pipeline: end-to-end pairs trading backtest.

Workflow:
  1. Generate/load market data universe
  2. Scan for cointegrated pairs (Johansen test)
  3. Initialize Kalman filters per pair
  4. Run daily simulation: signals → execution → P&L
  5. Report performance metrics + monitoring stats
"""

import time
import numpy as np
import pandas as pd
import structlog
from typing import Optional

from src.config import config, Config
from src.data.market_data import DataGenerator
from src.signals.cointegration import CointegrationScanner
from src.signals.signal_generator import SignalGenerator, SignalType
from src.execution.engine import ExecutionEngine
from src.monitoring.monitor import MonitoringService
from src.utils.metrics import compute_metrics, print_metrics

logger = structlog.get_logger()


class PairsTradingPipeline:
    """End-to-end pairs trading backtest pipeline."""

    def __init__(self, cfg: Optional[Config] = None):
        self.cfg = cfg or config

    def run(
        self,
        n_pairs: int = 30,
        n_noise: int = 20,
        n_days: int = 756,
        seed: int = 42,
        train_pct: float = 0.33,
    ):
        """Run full pairs trading backtest."""
        t0 = time.perf_counter()

        print(f"\n{'='*60}")
        print(f"  STATISTICAL ARBITRAGE PAIRS TRADING")
        print(f"{'='*60}")
        print(f"  Universe: {n_pairs} cointegrated pairs + {n_noise} noise stocks")
        print(f"  Period: {n_days} trading days (~{n_days/252:.1f} years)")
        print(f"  Capital: ${self.cfg.trading.initial_capital:,.0f}")
        print(f"{'='*60}\n")

        # --- Step 1: Generate data ---
        logger.info("generating_data")
        prices, true_pairs = DataGenerator.generate_universe(n_pairs, n_noise, n_days, seed)
        print(f"✓ Generated {len(prices.columns)} symbols x {n_days} days")

        # --- Step 2: Train/test split ---
        split_idx = int(len(prices) * train_pct)
        train_prices = prices.iloc[:split_idx]
        test_prices = prices.iloc[split_idx:]
        print(f"✓ Train: {len(train_prices)} days | Test: {len(test_prices)} days")

        # --- Step 3: Scan for cointegrated pairs (on training data) ---
        logger.info("scanning_pairs")
        scanner = CointegrationScanner(self.cfg.coint)
        pairs = scanner.scan(train_prices)
        print(f"✓ Found {len(pairs)} cointegrated pairs (from {len(true_pairs)} true pairs)")

        if not pairs:
            print("No cointegrated pairs found. Exiting.")
            return None

        # Print top pairs
        print(f"\n  Top 10 Pairs:")
        print(f"  {'Pair':<25} {'Beta':>6} {'HL':>5} {'Trace':>7} {'ADF-p':>7} {'Score':>7}")
        print(f"  {'-'*60}")
        for p in pairs[:10]:
            print(f"  {p.symbol_a}/{p.symbol_b:<16} {p.hedge_ratio:>6.2f} "
                  f"{p.half_life:>5.1f} {p.trace_stat:>7.1f} {p.adf_pvalue:>7.4f} {p.score:>7.2f}")

        # --- Step 4: Run backtest on test data ---
        logger.info("running_backtest")
        signal_gen = SignalGenerator(pairs, self.cfg.trading)
        executor = ExecutionEngine(self.cfg.trading)
        monitor = MonitoringService(
            self.cfg.monitoring.alert_latency_ms,
            self.cfg.monitoring.alert_drawdown_pct,
        )

        print(f"\n  Running backtest on {len(test_prices)} days...")
        ticks_processed = 0
        bt_start = time.perf_counter()

        for i, date in enumerate(test_prices.index):
            row_prices = {}
            for sym in test_prices.columns:
                row_prices[sym] = test_prices.loc[date, sym]

            # Generate signals for all pairs
            signals = signal_gen.process_bar(test_prices, date)

            for sig in signals:
                pa = row_prices.get(sig.symbol_a, 0)
                pb = row_prices.get(sig.symbol_b, 0)
                if pa > 0 and pb > 0:
                    executor.execute_signal(sig, pa, pb)
                    monitor.record_signal(sig.latency_ms, sig.signal_type.value)

            # Mark to market
            executor.mark_to_market(row_prices, date)
            monitor.check_drawdown(executor.snapshots[-1].drawdown if executor.snapshots else 0)

            ticks_processed += len(test_prices.columns)

            # Progress
            if (i + 1) % 100 == 0:
                eq = executor.snapshots[-1].equity if executor.snapshots else 0
                print(f"    Day {i+1}/{len(test_prices)}: equity=${eq:,.0f} | "
                      f"positions={executor.snapshots[-1].n_positions} | "
                      f"trades={len(executor.trades)}")

        bt_elapsed = time.perf_counter() - bt_start

        # --- Step 5: Results ---
        metrics = compute_metrics(
            executor.snapshots, executor.trades,
            ticks_processed, bt_elapsed,
        )
        print_metrics(metrics)
        monitor.print_report()

        # Detection accuracy
        detected_true = 0
        for p in pairs:
            for tp in true_pairs:
                if (p.symbol_a == tp[0] and p.symbol_b == tp[1]) or \
                   (p.symbol_a == tp[1] and p.symbol_b == tp[0]):
                    detected_true += 1
                    break

        print(f"  Pair Detection: {detected_true}/{len(pairs)} identified are true pairs "
              f"({detected_true/len(pairs)*100:.0f}% precision)")

        total_elapsed = time.perf_counter() - t0
        print(f"  Total runtime: {total_elapsed:.1f}s\n")

        return {
            "metrics": metrics,
            "pairs": pairs,
            "trades": executor.trades,
            "snapshots": executor.snapshots,
            "monitoring": monitor.summary(),
        }


def main():
    """Entry point."""
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(30),  # WARNING+
    )

    pipeline = PairsTradingPipeline()
    result = pipeline.run(n_pairs=30, n_noise=20, n_days=756, seed=42)

    if result:
        # Export equity curve
        snaps = result["snapshots"]
        df = pd.DataFrame([{
            "date": s.timestamp, "equity": s.equity, "cash": s.cash,
            "drawdown": s.drawdown, "n_positions": s.n_positions,
        } for s in snaps])
        df.to_csv("output/equity_curve.csv", index=False)

        # Export trades
        trades = result["trades"]
        td = pd.DataFrame([{
            "pair": t.pair_id, "direction": t.direction,
            "entry": t.entry_time, "exit": t.exit_time,
            "pnl": t.pnl, "return": t.return_pct,
            "holding_days": t.holding_days, "exit_reason": t.exit_reason,
        } for t in trades])
        td.to_csv("output/trades.csv", index=False)
        print("Exported: output/equity_curve.csv, output/trades.csv")


if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)
    main()
