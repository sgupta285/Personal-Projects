from __future__ import annotations

from pathlib import Path

from portfolio_risk.data_loader import load_positions, load_prices, load_targets
from portfolio_risk.optimizer import OptimizationConstraints, solve_min_variance
from portfolio_risk.portfolio import portfolio_snapshot
from portfolio_risk.rebalancer import generate_rebalancing_plan
from portfolio_risk.risk import covariance_matrix, return_matrix

ROOT = Path(__file__).resolve().parents[1]


def test_optimizer_weights_sum_to_one() -> None:
    prices = load_prices(ROOT / "data/raw/prices.csv")
    positions = load_positions(ROOT / "data/raw/positions.csv")
    targets = load_targets(ROOT / "data/raw/targets.csv")
    snapshot = portfolio_snapshot(prices, positions, targets)
    returns = return_matrix(prices)
    covariance = covariance_matrix(returns)
    weights = solve_min_variance(covariance, snapshot.set_index("ticker")["current_weight"], OptimizationConstraints())
    assert abs(float(weights.sum()) - 1.0) < 1e-6
    assert (weights >= 0).all()


def test_rebalancing_plan_contains_action_labels() -> None:
    prices = load_prices(ROOT / "data/raw/prices.csv")
    positions = load_positions(ROOT / "data/raw/positions.csv")
    targets = load_targets(ROOT / "data/raw/targets.csv")
    snapshot = portfolio_snapshot(prices, positions, targets)
    weights = snapshot.set_index("ticker")["target_weight"]
    plan = generate_rebalancing_plan(snapshot, weights, drift_threshold_bps=10.0)
    assert plan
    assert all(trade.action in {"buy", "sell"} for trade in plan)
