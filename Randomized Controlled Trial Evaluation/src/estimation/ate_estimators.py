"""
ATE / ITT Estimation.

Implements:
1. Difference-in-Means (Neyman estimator) — ITT
2. Lin (2013) Regression Adjustment — covariate-adjusted ATE
3. CUPED — pre-experiment variance reduction
4. Non-parametric Bootstrap confidence intervals
5. Fisher Randomization Inference (permutation test)
"""

import numpy as np
import pandas as pd
from scipy import stats
from dataclasses import dataclass
from typing import List, Optional, Tuple
import statsmodels.api as sm
import structlog

logger = structlog.get_logger()


@dataclass
class ATEResult:
    method: str
    estimate: float
    std_error: float
    ci_lower: float
    ci_upper: float
    p_value: float
    t_statistic: float
    n_treatment: int
    n_control: int
    variance_reduction_pct: float
    true_value: Optional[float] = None
    estimation_error: Optional[float] = None


def difference_in_means(
    df: pd.DataFrame, outcome: str = "outcome",
    treatment: str = "assigned_treatment",
    true_value: Optional[float] = None, alpha: float = 0.05,
) -> ATEResult:
    """Neyman difference-in-means estimator (ITT)."""
    treat = df[df[treatment] == 1][outcome].values
    ctrl = df[df[treatment] == 0][outcome].values
    n_t, n_c = len(treat), len(ctrl)

    ate = treat.mean() - ctrl.mean()
    var = np.var(treat, ddof=1) / n_t + np.var(ctrl, ddof=1) / n_c
    se = np.sqrt(var)
    t_stat = ate / se if se > 0 else 0
    p_val = 2 * (1 - stats.norm.cdf(abs(t_stat)))
    z = stats.norm.ppf(1 - alpha / 2)
    ci = (round(ate - z * se, 4), round(ate + z * se, 4))
    err = abs(ate - true_value) if true_value is not None else None

    return ATEResult(
        method="Difference-in-Means (ITT)", estimate=round(ate, 4),
        std_error=round(se, 4), ci_lower=ci[0], ci_upper=ci[1],
        p_value=round(p_val, 6), t_statistic=round(t_stat, 3),
        n_treatment=n_t, n_control=n_c, variance_reduction_pct=0.0,
        true_value=true_value,
        estimation_error=round(err, 4) if err is not None else None,
    )


def lin_estimator(
    df: pd.DataFrame, outcome: str = "outcome",
    treatment: str = "assigned_treatment",
    covariates: List[str] = None,
    true_value: Optional[float] = None, alpha: float = 0.05,
) -> ATEResult:
    """
    Lin (2013) regression adjustment.

    Y = β₀ + τ·T + β·(X - X̄) + γ·T·(X - X̄) + ε

    Fully-interacted demeaned covariates. Consistent even if linear model
    is misspecified. HC2 robust SEs.
    """
    if covariates is None:
        covariates = ["age", "bmi", "pre_outcome", "biomarker_a"]

    data = df.copy()
    T = data[treatment].values
    Y = data[outcome].values

    available = [c for c in covariates if c in data.columns and data[c].dtype in (np.float64, np.int64, float, int)]
    X_raw = data[available].values.astype(float)
    X_demeaned = X_raw - X_raw.mean(axis=0)

    X_design = np.column_stack([np.ones(len(T)), T, X_demeaned, T[:, None] * X_demeaned])
    model = sm.OLS(Y, X_design).fit(cov_type="HC2")

    ate = model.params[1]
    se = model.bse[1]
    t_stat = model.tvalues[1]
    p_val = model.pvalues[1]
    z = stats.norm.ppf(1 - alpha / 2)
    ci = (round(ate - z * se, 4), round(ate + z * se, 4))

    naive = difference_in_means(df, outcome, treatment)
    var_red = max(0, 1 - (se ** 2) / (naive.std_error ** 2)) * 100
    err = abs(ate - true_value) if true_value is not None else None

    return ATEResult(
        method="Lin Regression Adjustment", estimate=round(ate, 4),
        std_error=round(se, 4), ci_lower=ci[0], ci_upper=ci[1],
        p_value=round(p_val, 6), t_statistic=round(t_stat, 3),
        n_treatment=int(T.sum()), n_control=int(len(T) - T.sum()),
        variance_reduction_pct=round(var_red, 1),
        true_value=true_value,
        estimation_error=round(err, 4) if err is not None else None,
    )


def cuped_estimator(
    df: pd.DataFrame, outcome: str = "outcome",
    treatment: str = "assigned_treatment",
    pre_metric: str = "pre_outcome",
    true_value: Optional[float] = None, alpha: float = 0.05,
) -> ATEResult:
    """
    CUPED: Y_adj = Y - θ·(X_pre - E[X_pre])
    where θ = Cov(Y, X_pre) / Var(X_pre).
    """
    Y = df[outcome].values
    X_pre = df[pre_metric].values
    T = df[treatment].values

    theta = np.cov(Y, X_pre)[0, 1] / max(np.var(X_pre, ddof=1), 1e-10)
    Y_adj = Y - theta * (X_pre - X_pre.mean())

    treat = Y_adj[T == 1]
    ctrl = Y_adj[T == 0]
    n_t, n_c = len(treat), len(ctrl)

    ate = treat.mean() - ctrl.mean()
    var = np.var(treat, ddof=1) / n_t + np.var(ctrl, ddof=1) / n_c
    se = np.sqrt(var)
    t_stat = ate / se if se > 0 else 0
    p_val = 2 * (1 - stats.norm.cdf(abs(t_stat)))
    z = stats.norm.ppf(1 - alpha / 2)
    ci = (round(ate - z * se, 4), round(ate + z * se, 4))

    naive = difference_in_means(df, outcome, treatment)
    var_red = max(0, 1 - (se ** 2) / (naive.std_error ** 2)) * 100
    err = abs(ate - true_value) if true_value is not None else None

    return ATEResult(
        method="CUPED", estimate=round(ate, 4),
        std_error=round(se, 4), ci_lower=ci[0], ci_upper=ci[1],
        p_value=round(p_val, 6), t_statistic=round(t_stat, 3),
        n_treatment=n_t, n_control=n_c,
        variance_reduction_pct=round(var_red, 1),
        true_value=true_value,
        estimation_error=round(err, 4) if err is not None else None,
    )


def bootstrap_ate(
    df: pd.DataFrame, outcome: str = "outcome",
    treatment: str = "assigned_treatment",
    n_bootstrap: int = 2000, alpha: float = 0.05, seed: int = 42,
) -> Tuple[float, float, float, np.ndarray]:
    """Non-parametric bootstrap with percentile CI."""
    np.random.seed(seed)
    n = len(df)
    boot_ates = np.zeros(n_bootstrap)
    for b in range(n_bootstrap):
        sample = df.sample(n, replace=True)
        t = sample[sample[treatment] == 1][outcome].values
        c = sample[sample[treatment] == 0][outcome].values
        boot_ates[b] = t.mean() - c.mean()

    return (round(boot_ates.mean(), 4),
            round(np.percentile(boot_ates, alpha / 2 * 100), 4),
            round(np.percentile(boot_ates, (1 - alpha / 2) * 100), 4),
            boot_ates)


def permutation_test(
    df: pd.DataFrame, outcome: str = "outcome",
    treatment: str = "assigned_treatment",
    n_permutations: int = 5000, seed: int = 42,
) -> Tuple[float, float, np.ndarray]:
    """Fisher randomization inference. Tests sharp null H₀: Y_i(1)=Y_i(0) ∀i."""
    np.random.seed(seed)
    Y = df[outcome].values
    T = df[treatment].values
    n_t = int(T.sum())

    observed = Y[T == 1].mean() - Y[T == 0].mean()
    perm_stats = np.zeros(n_permutations)
    for p in range(n_permutations):
        perm_T = np.zeros(len(T))
        perm_T[np.random.choice(len(T), n_t, replace=False)] = 1
        perm_stats[p] = Y[perm_T == 1].mean() - Y[perm_T == 0].mean()

    p_val = np.mean(np.abs(perm_stats) >= abs(observed))
    return round(observed, 4), round(p_val, 6), perm_stats
