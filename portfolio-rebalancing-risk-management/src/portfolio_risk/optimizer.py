from __future__ import annotations

from dataclasses import dataclass
import logging

import numpy as np
import pandas as pd

from .models import EfficientFrontierPoint

logger = logging.getLogger(__name__)

try:
    import cvxpy as cp  # type: ignore
except Exception:
    cp = None


@dataclass(slots=True)
class OptimizationConstraints:
    min_weight: float = 0.0
    max_weight: float = 0.40
    max_turnover: float = 0.15


def _normalize_nonnegative(weights: np.ndarray, min_weight: float, max_weight: float) -> np.ndarray:
    clipped = np.clip(weights, min_weight, max_weight)
    total = clipped.sum()
    if total <= 0:
        clipped[:] = 1.0 / len(clipped)
        return clipped
    clipped /= total
    for _ in range(20):
        overflow = clipped > max_weight
        underflow = clipped < min_weight
        if not overflow.any() and not underflow.any():
            break
        clipped = np.clip(clipped, min_weight, max_weight)
        clipped /= clipped.sum()
    return clipped


def fallback_min_variance(covariance: pd.DataFrame, current_weights: pd.Series, constraints: OptimizationConstraints) -> pd.Series:
    diag = np.diag(covariance.values)
    inv_vol = 1.0 / np.sqrt(np.maximum(diag, 1e-12))
    base = inv_vol / inv_vol.sum()
    current = current_weights.reindex(covariance.index).fillna(0.0).to_numpy()
    proposed = current + np.clip(base - current, -constraints.max_turnover, constraints.max_turnover)
    weights = _normalize_nonnegative(proposed, constraints.min_weight, constraints.max_weight)
    return pd.Series(weights, index=covariance.index)


def solve_min_variance(covariance: pd.DataFrame, current_weights: pd.Series, constraints: OptimizationConstraints) -> pd.Series:
    assets = list(covariance.index)
    current = current_weights.reindex(assets).fillna(0.0).to_numpy()
    if cp is None:
        logger.info("cvxpy unavailable, using fallback optimizer")
        return fallback_min_variance(covariance, current_weights, constraints)

    w = cp.Variable(len(assets))
    objective = cp.Minimize(cp.quad_form(w, covariance.values))
    problem_constraints = [
        cp.sum(w) == 1,
        w >= constraints.min_weight,
        w <= constraints.max_weight,
        cp.norm1(w - current) <= constraints.max_turnover,
    ]
    problem = cp.Problem(objective, problem_constraints)
    try:
        problem.solve(solver=cp.SCS, verbose=False)
    except Exception as exc:
        logger.warning("cvxpy solve failed, falling back: %s", exc)
        return fallback_min_variance(covariance, current_weights, constraints)

    if w.value is None:
        return fallback_min_variance(covariance, current_weights, constraints)
    weights = _normalize_nonnegative(np.asarray(w.value).ravel(), constraints.min_weight, constraints.max_weight)
    return pd.Series(weights, index=assets)


def efficient_frontier(expected_returns: pd.Series, covariance: pd.DataFrame, constraints: OptimizationConstraints, points: int = 8) -> list[EfficientFrontierPoint]:
    assets = list(expected_returns.index)
    mu = expected_returns.to_numpy()
    cov = covariance.loc[assets, assets].to_numpy()
    target_returns = np.linspace(mu.min(), mu.max(), points)
    frontier: list[EfficientFrontierPoint] = []

    for target in target_returns:
        if cp is None:
            weights = fallback_min_variance(covariance.loc[assets, assets], pd.Series(np.repeat(1/len(assets), len(assets)), index=assets), constraints)
        else:
            w = cp.Variable(len(assets))
            objective = cp.Minimize(cp.quad_form(w, cov))
            cons = [
                cp.sum(w) == 1,
                w >= constraints.min_weight,
                w <= constraints.max_weight,
                mu @ w >= target,
            ]
            problem = cp.Problem(objective, cons)
            try:
                problem.solve(solver=cp.SCS, verbose=False)
            except Exception:
                weights = fallback_min_variance(covariance.loc[assets, assets], pd.Series(np.repeat(1/len(assets), len(assets)), index=assets), constraints)
            else:
                if w.value is None:
                    weights = fallback_min_variance(covariance.loc[assets, assets], pd.Series(np.repeat(1/len(assets), len(assets)), index=assets), constraints)
                else:
                    arr = _normalize_nonnegative(np.asarray(w.value).ravel(), constraints.min_weight, constraints.max_weight)
                    weights = pd.Series(arr, index=assets)

        annual_return = float(expected_returns.loc[assets].dot(weights.loc[assets]))
        vol = float(np.sqrt(weights.loc[assets].to_numpy() @ cov @ weights.loc[assets].to_numpy()))
        frontier.append(EfficientFrontierPoint(expected_return=annual_return, annualized_volatility=vol, weights=weights.to_dict()))
    return frontier
