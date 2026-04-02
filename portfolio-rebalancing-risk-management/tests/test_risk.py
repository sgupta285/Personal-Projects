from __future__ import annotations

from pathlib import Path

from portfolio_risk.data_loader import load_positions, load_prices, load_targets
from portfolio_risk.portfolio import portfolio_snapshot
from portfolio_risk.risk import correlation_matrix, return_matrix, risk_snapshot

ROOT = Path(__file__).resolve().parents[1]


def test_risk_snapshot_is_positive() -> None:
    prices = load_prices(ROOT / "data/raw/prices.csv")
    positions = load_positions(ROOT / "data/raw/positions.csv")
    targets = load_targets(ROOT / "data/raw/targets.csv")
    snapshot = portfolio_snapshot(prices, positions, targets)
    returns = return_matrix(prices)
    metrics = risk_snapshot(returns, snapshot, 0.02, 0.95)
    assert metrics.portfolio_value > 0
    assert metrics.daily_var > 0
    assert metrics.daily_cvar >= metrics.daily_var
    assert metrics.annualized_volatility > 0


def test_correlation_matrix_diagonal_is_one() -> None:
    prices = load_prices(ROOT / "data/raw/prices.csv")
    corr = correlation_matrix(return_matrix(prices))
    for ticker in corr.columns:
        assert round(float(corr.loc[ticker, ticker]), 5) == 1.0
