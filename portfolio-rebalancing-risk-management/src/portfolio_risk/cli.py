from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from .config import Settings
from .data_loader import load_positions, load_prices, load_targets
from .logging_utils import configure_logging
from .optimizer import OptimizationConstraints, efficient_frontier, solve_min_variance
from .portfolio import portfolio_snapshot
from .rebalancer import generate_rebalancing_plan
from .reports import write_report
from .risk import correlation_matrix, covariance_matrix, expected_asset_returns, return_matrix, risk_snapshot
from .storage import persist_risk_snapshot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Portfolio rebalancing and risk management toolkit")
    parser.add_argument("--prices", default="data/raw/prices.csv")
    parser.add_argument("--positions", default="data/raw/positions.csv")
    parser.add_argument("--targets", default="data/raw/targets.csv")
    parser.add_argument("--report-dir", default="artifacts/demo")
    return parser


def main() -> None:
    configure_logging()
    args = build_parser().parse_args()
    settings = Settings()

    prices = load_prices(args.prices)
    positions = load_positions(args.positions)
    targets = load_targets(args.targets)
    snapshot = portfolio_snapshot(prices, positions, targets)

    returns = return_matrix(prices)
    expected = expected_asset_returns(returns, settings.trading_days)
    covariance = covariance_matrix(returns, settings.trading_days)
    correlation = correlation_matrix(returns)
    risk = risk_snapshot(returns, snapshot, settings.risk_free_rate, settings.var_confidence, settings.trading_days)

    constraints = OptimizationConstraints(
        min_weight=settings.min_weight,
        max_weight=settings.max_weight,
        max_turnover=settings.max_turnover,
    )
    optimized = solve_min_variance(covariance, snapshot.set_index("ticker")["current_weight"], constraints)
    frontier = efficient_frontier(expected, covariance, constraints)
    plan = generate_rebalancing_plan(snapshot, optimized)

    out = write_report(args.report_dir, risk, snapshot, plan, frontier, correlation)
    persist_risk_snapshot(str(prices["date"].max().date()), risk, settings.database_url)

    print(json.dumps({
        "report_path": str(out),
        "portfolio_value": round(risk.portfolio_value, 2),
        "daily_var": round(risk.daily_var, 6),
        "daily_cvar": round(risk.daily_cvar, 6),
        "volatility": round(risk.annualized_volatility, 6),
        "recommendations": len(plan),
    }, indent=2))


if __name__ == "__main__":
    main()
