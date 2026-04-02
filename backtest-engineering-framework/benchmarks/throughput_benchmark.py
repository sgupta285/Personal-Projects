from __future__ import annotations

from dataclasses import asdict
import time

from backtest_engineering.config import load_config
from backtest_engineering.data import load_prices
from backtest_engineering.engine import run_backtest
from backtest_engineering.execution import ExecutionParams


def main() -> None:
    cfg = load_config("configs/momentum_walk_forward.yaml")
    prices = load_prices(cfg.data_path, cfg.tickers)
    params = ExecutionParams(**asdict(cfg.execution))
    iterations = 20

    start = time.perf_counter()
    for _ in range(iterations):
        run_backtest(
            prices,
            params,
            cfg.strategy.short_window,
            cfg.strategy.long_window,
            cfg.strategy.volatility_lookback,
            cfg.strategy.target_gross_leverage,
            cfg.initial_capital,
        )
    elapsed = time.perf_counter() - start
    print({
        "iterations": iterations,
        "elapsed_seconds": round(elapsed, 4),
        "backtests_per_second": round(iterations / elapsed, 3),
    })


if __name__ == "__main__":
    main()
