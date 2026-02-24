"""
RCT Diagnostics.

Implements:
1. Covariate balance table (SMD, KS test, normalized differences)
2. Attrition analysis (differential attrition, Lee bounds)
3. Multiple testing correction (Bonferroni, Holm, BH)
4. Power analysis and minimum detectable effect
"""

import numpy as np
import pandas as pd
from scipy import stats
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import structlog

logger = structlog.get_logger()


# ============================================================
# COVARIATE BALANCE
# ============================================================

@dataclass
class BalanceRow:
    covariate: str
    mean_treatment: float
    mean_control: float
    smd: float                   # Standardized Mean Difference
    p_value: float               # t-test or chi-squared
    balanced: bool               # |SMD| < threshold


@dataclass
class BalanceTable:
    rows: List[BalanceRow]
    n_treatment: int
    n_control: int
    n_imbalanced: int
    overall_balanced: bool       # All covariates balanced
    max_smd: float
    joint_f_stat: float          # Joint F-test: all covariates predict treatment?
    joint_f_p: float


def covariate_balance(
    df: pd.DataFrame,
    treatment: str = "assigned_treatment",
    covariates: Optional[List[str]] = None,
    smd_threshold: float = 0.10,
) -> BalanceTable:
    """
    Covariate balance table for RCT validation.

    SMD = (mean_T - mean_C) / sqrt((var_T + var_C) / 2)
    |SMD| < 0.10 → acceptable balance (Imbens & Rubin threshold).
    """
    if covariates is None:
        covariates = ["age", "bmi", "pre_outcome", "biomarker_a", "biomarker_b"]
    available = [c for c in covariates if c in df.columns
                 and df[c].dtype in (np.float64, np.int64, float, int)]

    treat = df[df[treatment] == 1]
    ctrl = df[df[treatment] == 0]
    n_t, n_c = len(treat), len(ctrl)

    rows = []
    for cov in available:
        t_vals = treat[cov].values.astype(float)
        c_vals = ctrl[cov].values.astype(float)

        pooled_std = np.sqrt((np.var(t_vals, ddof=1) + np.var(c_vals, ddof=1)) / 2)
        smd = (t_vals.mean() - c_vals.mean()) / pooled_std if pooled_std > 0 else 0

        _, p = stats.ttest_ind(t_vals, c_vals, equal_var=False)

        rows.append(BalanceRow(
            covariate=cov,
            mean_treatment=round(t_vals.mean(), 3),
            mean_control=round(c_vals.mean(), 3),
            smd=round(smd, 4),
            p_value=round(p, 6),
            balanced=abs(smd) < smd_threshold,
        ))

    n_imbalanced = sum(1 for r in rows if not r.balanced)
    max_smd = max(abs(r.smd) for r in rows) if rows else 0

    # Joint F-test: regress treatment on all covariates
    import statsmodels.api as sm
    X = sm.add_constant(df[available].values.astype(float))
    T = df[treatment].values.astype(float)
    joint_model = sm.OLS(T, X).fit()
    joint_f = joint_model.fvalue
    joint_p = joint_model.f_pvalue

    return BalanceTable(
        rows=rows, n_treatment=n_t, n_control=n_c,
        n_imbalanced=n_imbalanced,
        overall_balanced=n_imbalanced == 0,
        max_smd=round(max_smd, 4),
        joint_f_stat=round(float(joint_f), 3),
        joint_f_p=round(float(joint_p), 6),
    )


# ============================================================
# ATTRITION ANALYSIS
# ============================================================

@dataclass
class AttritionResult:
    overall_rate: float
    treatment_rate: float
    control_rate: float
    differential: float          # Treatment attrition - Control attrition
    differential_p: float        # Test for differential attrition
    is_differential: bool
    lee_bounds: Optional[Tuple[float, float]] = None  # Lee (2009) trimming bounds


def attrition_analysis(
    df: pd.DataFrame,
    outcome: str = "outcome",
    treatment: str = "assigned_treatment",
    attrition_col: str = "attrited",
) -> AttritionResult:
    """
    Analyze attrition and compute Lee (2009) trimming bounds.

    Lee bounds: trim the group with less attrition to equalize attrition rates,
    then compute upper/lower bounds on ATE by trimming from above/below.
    """
    T = df[treatment].values
    A = df[attrition_col].values.astype(bool)

    overall_rate = A.mean()
    treat_rate = A[T == 1].mean()
    ctrl_rate = A[T == 0].mean()
    diff = treat_rate - ctrl_rate

    # Test for differential attrition
    _, diff_p = stats.proportions_ztest(
        [A[T == 1].sum(), A[T == 0].sum()],
        [(T == 1).sum(), (T == 0).sum()],
    )

    # Lee bounds
    lee_bounds = _compute_lee_bounds(df, outcome, treatment, attrition_col)

    return AttritionResult(
        overall_rate=round(overall_rate, 4),
        treatment_rate=round(treat_rate, 4),
        control_rate=round(ctrl_rate, 4),
        differential=round(diff, 4),
        differential_p=round(diff_p, 6),
        is_differential=diff_p < 0.05,
        lee_bounds=lee_bounds,
    )


def _compute_lee_bounds(
    df: pd.DataFrame,
    outcome: str, treatment: str, attrition_col: str,
) -> Optional[Tuple[float, float]]:
    """
    Lee (2009) trimming bounds for ATE under selective attrition.

    Trim the less-attrited group to equalize attrition rates.
    Lower bound: trim top outcomes from less-attrited group.
    Upper bound: trim bottom outcomes from less-attrited group.
    """
    observed = df[~df[attrition_col].astype(bool)].copy()
    T = df[treatment].values
    A = df[attrition_col].values.astype(bool)

    n_t = (T == 1).sum()
    n_c = (T == 0).sum()
    n_t_obs = ((T == 1) & ~A).sum()
    n_c_obs = ((T == 0) & ~A).sum()

    # Which group has less attrition?
    rate_t = 1 - n_t_obs / n_t
    rate_c = 1 - n_c_obs / n_c

    if abs(rate_t - rate_c) < 0.001:
        # No differential attrition → standard estimate
        treat_y = observed[observed[treatment] == 1][outcome].values
        ctrl_y = observed[observed[treatment] == 0][outcome].values
        est = treat_y.mean() - ctrl_y.mean()
        return (round(est, 4), round(est, 4))

    # Determine which group to trim
    if rate_t < rate_c:
        # Treatment has less attrition → trim treatment
        trim_group = "treatment"
        excess = n_t_obs - int(n_t * (1 - rate_c))
        trim_y = observed[observed[treatment] == 1][outcome].sort_values()
        other_y = observed[observed[treatment] == 0][outcome].values
    else:
        trim_group = "control"
        excess = n_c_obs - int(n_c * (1 - rate_t))
        trim_y = observed[observed[treatment] == 0][outcome].sort_values()
        other_y = observed[observed[treatment] == 1][outcome].values

    if excess <= 0 or len(trim_y) <= excess:
        return None

    # Lower bound: trim from top of trim_group
    trimmed_lower = trim_y.values[:len(trim_y) - excess]
    # Upper bound: trim from bottom
    trimmed_upper = trim_y.values[excess:]

    if trim_group == "treatment":
        lower = trimmed_lower.mean() - other_y.mean()
        upper = trimmed_upper.mean() - other_y.mean()
    else:
        lower = other_y.mean() - trimmed_upper.mean()
        upper = other_y.mean() - trimmed_lower.mean()

    return (round(min(lower, upper), 4), round(max(lower, upper), 4))


# ============================================================
# MULTIPLE TESTING CORRECTION
# ============================================================

def bonferroni(p_values: List[float], alpha: float = 0.05) -> List[Tuple[float, bool]]:
    m = len(p_values)
    threshold = alpha / m
    return [(p, p < threshold) for p in p_values]


def holm_correction(p_values: List[float], alpha: float = 0.05) -> List[Tuple[float, bool]]:
    m = len(p_values)
    idx = np.argsort(p_values)
    results = [None] * m
    rejected = True
    for rank, i in enumerate(idx):
        threshold = alpha / (m - rank)
        if rejected and p_values[i] < threshold:
            results[i] = (p_values[i], True)
        else:
            rejected = False
            results[i] = (p_values[i], False)
    return results


def benjamini_hochberg(p_values: List[float], alpha: float = 0.05) -> List[Tuple[float, bool]]:
    """Benjamini-Hochberg FDR control."""
    m = len(p_values)
    idx = np.argsort(p_values)
    results = [None] * m
    last_reject = -1
    for rank, i in enumerate(idx):
        threshold = alpha * (rank + 1) / m
        if p_values[i] <= threshold:
            last_reject = rank
    for rank, i in enumerate(idx):
        results[i] = (p_values[i], rank <= last_reject)
    return results


# ============================================================
# POWER ANALYSIS
# ============================================================

@dataclass
class PowerResult:
    sample_size_per_arm: int
    total_sample_size: int
    mde: float
    power: float
    alpha: float
    baseline_mean: float
    baseline_std: float


def power_analysis(
    baseline_mean: float = 50.0,
    baseline_std: float = 10.0,
    mde: float = 2.0,
    alpha: float = 0.05,
    power: float = 0.80,
) -> PowerResult:
    """Compute required sample size for two-arm RCT."""
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)

    n_per_arm = int(np.ceil(2 * (baseline_std ** 2) * (z_alpha + z_beta) ** 2 / mde ** 2))

    return PowerResult(
        sample_size_per_arm=n_per_arm,
        total_sample_size=2 * n_per_arm,
        mde=mde, power=power, alpha=alpha,
        baseline_mean=baseline_mean,
        baseline_std=baseline_std,
    )
