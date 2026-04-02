from __future__ import annotations

from dataclasses import asdict
import argparse
from pathlib import Path

import pandas as pd

from backtest_engineering.config import load_config
from backtest_engineering.data import load_prices
from backtest_engineering.engine import run_backtest
from backtest_engineering.execution import ExecutionParams
from backtest_engineering.metrics import holm_bonferroni


def main() -> None:
    parser = argparse.ArgumentParser(description="Run parameter sweep for a backtest")
    parser.add_argument("--config", default="configs/momentum_walk_forward.yaml")
    args = parser.parse_args()

    cfg = load_config(args.config)
    prices = load_prices(cfg.data_path, cfg.tickers)
    rows: list[dict] = []
    execution_params = ExecutionParams(**asdict(cfg.execution))
    for short_window in cfg.sweep.short_windows:
        for long_window in cfg.sweep.long_windows:
            if short_window >= long_window:
                continue
            result = run_backtest(
                prices,
                execution_params,
                short_window,
                long_window,
                cfg.strategy.volatility_lookback,
                cfg.strategy.target_gross_leverage,
                cfg.initial_capital,
            )
            rows.append({
                "short_window": short_window,
                "long_window": long_window,
                **result.summary,
            })
    leaderboard = pd.DataFrame(rows).sort_values(["sharpe_ratio", "annualized_return"], ascending=False).reset_index(drop=True)
    leaderboard["adjusted_p_value"] = holm_bonferroni(leaderboard["p_value"].tolist())
    out_path = Path(cfg.output_dir) / "parameter_sweep.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    leaderboard.to_csv(out_path, index=False)
    print(leaderboard.head(10).to_string(index=False))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
