from __future__ import annotations

from dataclasses import asdict
import argparse
from pathlib import Path

from backtest_engineering.config import load_config
from backtest_engineering.data import load_prices
from backtest_engineering.execution import ExecutionParams
from backtest_engineering.reporting import plot_equity_curve, write_csv, write_summary_json
from backtest_engineering.walk_forward import run_walk_forward


def main() -> None:
    parser = argparse.ArgumentParser(description="Run walk-forward backtest with execution realism")
    parser.add_argument("--config", default="configs/momentum_walk_forward.yaml")
    args = parser.parse_args()

    cfg = load_config(args.config)
    prices = load_prices(cfg.data_path, cfg.tickers)
    output_dir = Path(cfg.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    result = run_walk_forward(
        prices=prices,
        execution_params=ExecutionParams(**asdict(cfg.execution)),
        sweep_short_windows=cfg.sweep.short_windows,
        sweep_long_windows=cfg.sweep.long_windows,
        volatility_lookback=cfg.strategy.volatility_lookback,
        target_gross_leverage=cfg.strategy.target_gross_leverage,
        train_days=cfg.walk_forward.train_days,
        test_days=cfg.walk_forward.test_days,
        step_days=cfg.walk_forward.step_days,
        initial_capital=cfg.initial_capital,
    )

    write_summary_json(result.stitched_result.summary, output_dir / "summary.json")
    write_csv(result.leaderboard, output_dir / "walk_forward_folds.csv")
    write_csv(result.stitched_result.trade_log, output_dir / "trade_log.csv")
    plot_equity_curve(result.stitched_result.equity_curve, output_dir / "equity_curve.png")
    print("best_params", result.best_params)
    print("summary", result.stitched_result.summary)


if __name__ == "__main__":
    main()
