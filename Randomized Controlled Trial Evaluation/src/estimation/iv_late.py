"""
LATE / IV Estimation via Two-Stage Least Squares.

Under non-compliance, assignment Z is an instrument for actual treatment D.
LATE = E[Y(1)-Y(0) | complier] identified via:

  Wald estimator:  LATE = ITT_Y / ITT_D
  2SLS:            Stage 1: D = π₀ + π₁Z + π₂X + v
                   Stage 2: Y = β₀ + τD̂ + β₁X + ε

Implements:
1. Wald (ratio) estimator with delta-method SE
2. Manual 2SLS with covariates
3. First-stage diagnostics (F-stat, partial R²)
4. Hausman endogeneity test (OLS vs IV)
5. Compliance-type analysis
"""

import numpy as np
import pandas as pd
from scipy import stats
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
import statsmodels.api as sm
import structlog

logger = structlog.get_logger()


@dataclass
class FirstStageDiagnostics:
    f_statistic: float
    f_p_value: float
    partial_r_squared: float
    instrument_coef: float
    instrument_se: float
    instrument_t: float
    is_strong: bool              # F > 10 (Staiger-Stock rule of thumb)
    compliance_rate: float       # E[D|Z=1] - E[D|Z=0]


@dataclass
class LATEResult:
    method: str
    estimate: float
    std_error: float
    ci_lower: float
    ci_upper: float
    p_value: float
    t_statistic: float
    n_observations: int
    first_stage: FirstStageDiagnostics
    true_late: Optional[float] = None
    estimation_error: Optional[float] = None


@dataclass
class HausmanResult:
    ols_estimate: float
    iv_estimate: float
    test_statistic: float
    p_value: float
    endogeneity_detected: bool
    interpretation: str


@dataclass
class ComplianceAnalysis:
    n_total: int
    n_compliers_est: int
    n_always_takers_est: int
    n_never_takers_est: int
    complier_share: float
    always_taker_share: float
    never_taker_share: float
    # If oracle compliance_type column available
    oracle_available: bool
    oracle_accuracy: Optional[float] = None


# ============================================================
# WALD (RATIO) ESTIMATOR
# ============================================================

def wald_estimator(
    df: pd.DataFrame,
    outcome: str = "outcome",
    assignment: str = "assigned_treatment",
    treatment: str = "actual_treatment",
    true_late: Optional[float] = None,
    alpha: float = 0.05,
) -> LATEResult:
    """
    Wald (ratio) estimator for LATE.

    LATE = [E(Y|Z=1) - E(Y|Z=0)] / [E(D|Z=1) - E(D|Z=0)]
         = ITT_Y / ITT_D

    SE via delta method: Var(LATE) ≈ Var(ITT_Y)/ITT_D² + ITT_Y²·Var(ITT_D)/ITT_D⁴
    """
    Z = df[assignment].values
    D = df[treatment].values
    Y = df[outcome].values

    n1 = (Z == 1).sum()
    n0 = (Z == 0).sum()

    # ITT on outcome
    y1_bar = Y[Z == 1].mean()
    y0_bar = Y[Z == 0].mean()
    itt_y = y1_bar - y0_bar

    # First stage (ITT on treatment take-up)
    d1_bar = D[Z == 1].mean()
    d0_bar = D[Z == 0].mean()
    itt_d = d1_bar - d0_bar

    # First-stage diagnostics
    first_stage_diag = _compute_first_stage(df, assignment, treatment)

    if abs(itt_d) < 0.01:
        logger.warning("weak_first_stage", itt_d=itt_d)
        return LATEResult(
            method="Wald (Ratio)", estimate=0, std_error=999,
            ci_lower=-999, ci_upper=999, p_value=1.0, t_statistic=0,
            n_observations=len(Y), first_stage=first_stage_diag,
            true_late=true_late,
        )

    late = itt_y / itt_d

    # Delta method SE
    var_y = np.var(Y[Z == 1], ddof=1) / n1 + np.var(Y[Z == 0], ddof=1) / n0
    var_d = np.var(D[Z == 1], ddof=1) / n1 + np.var(D[Z == 0], ddof=1) / n0
    # Cov(ITT_Y, ITT_D) via sample analogue
    cov_yd = (np.cov(Y[Z == 1], D[Z == 1])[0, 1] / n1
              + np.cov(Y[Z == 0], D[Z == 0])[0, 1] / n0)

    var_late = (var_y / itt_d ** 2
                - 2 * itt_y * cov_yd / itt_d ** 3
                + itt_y ** 2 * var_d / itt_d ** 4)
    se = np.sqrt(max(var_late, 1e-10))

    t_stat = late / se
    p_val = 2 * (1 - stats.norm.cdf(abs(t_stat)))
    z = stats.norm.ppf(1 - alpha / 2)
    ci = (round(late - z * se, 4), round(late + z * se, 4))
    err = abs(late - true_late) if true_late is not None else None

    return LATEResult(
        method="Wald (Ratio)", estimate=round(late, 4),
        std_error=round(se, 4), ci_lower=ci[0], ci_upper=ci[1],
        p_value=round(p_val, 6), t_statistic=round(t_stat, 3),
        n_observations=len(Y), first_stage=first_stage_diag,
        true_late=true_late,
        estimation_error=round(err, 4) if err is not None else None,
    )


# ============================================================
# MANUAL 2SLS WITH COVARIATES
# ============================================================

def tsls_estimator(
    df: pd.DataFrame,
    outcome: str = "outcome",
    treatment: str = "actual_treatment",
    instrument: str = "assigned_treatment",
    covariates: Optional[List[str]] = None,
    true_late: Optional[float] = None,
    alpha: float = 0.05,
) -> LATEResult:
    """
    Manual two-stage least squares with covariates.

    Stage 1: D = π₀ + π₁Z + π₂X + v       (predict treatment from instrument + controls)
    Stage 2: Y = β₀ + τD̂ + β₁X + ε         (regress outcome on predicted treatment + controls)

    SE correction: use Stage-2 residuals computed from actual D (not D̂)
    to get correct standard errors.
    """
    data = df.copy()
    Y = data[outcome].values
    D = data[treatment].values
    Z = data[instrument].values

    if covariates is None:
        covariates = ["age", "bmi", "pre_outcome", "biomarker_a"]
    available = [c for c in covariates if c in data.columns
                 and data[c].dtype in (np.float64, np.int64, float, int)]

    X_ctrl = data[available].values.astype(float) if available else np.empty((len(Y), 0))

    # ── Stage 1: D on Z + X ──
    X1 = np.column_stack([np.ones(len(Z)), Z, X_ctrl]) if X_ctrl.shape[1] > 0 else np.column_stack([np.ones(len(Z)), Z])
    stage1 = sm.OLS(D, X1).fit()
    D_hat = stage1.fittedvalues

    # First-stage F on excluded instrument
    first_stage_diag = _compute_first_stage(df, instrument, treatment, available)

    # ── Stage 2: Y on D̂ + X ──
    X2 = np.column_stack([np.ones(len(Y)), D_hat, X_ctrl]) if X_ctrl.shape[1] > 0 else np.column_stack([np.ones(len(Y)), D_hat])
    stage2 = sm.OLS(Y, X2).fit()

    tau_hat = stage2.params[1]

    # ── SE Correction ──
    # Residuals from actual D (not D̂)
    X2_actual = np.column_stack([np.ones(len(Y)), D, X_ctrl]) if X_ctrl.shape[1] > 0 else np.column_stack([np.ones(len(Y)), D])
    residuals_corrected = Y - X2_actual @ np.array([stage2.params[0], tau_hat] + list(stage2.params[2:]))

    n = len(Y)
    k = X2.shape[1]
    sigma2 = np.sum(residuals_corrected ** 2) / (n - k)

    # Variance of τ̂: σ² · (X₂'X₂)⁻¹[1,1] but using D̂ projector
    XtX_inv = np.linalg.inv(X2.T @ X2)
    se_corrected = np.sqrt(sigma2 * XtX_inv[1, 1])

    t_stat = tau_hat / se_corrected
    p_val = 2 * (1 - stats.t.cdf(abs(t_stat), n - k))
    z = stats.norm.ppf(1 - alpha / 2)
    ci = (round(tau_hat - z * se_corrected, 4), round(tau_hat + z * se_corrected, 4))
    err = abs(tau_hat - true_late) if true_late is not None else None

    return LATEResult(
        method="2SLS (Manual)", estimate=round(tau_hat, 4),
        std_error=round(se_corrected, 4), ci_lower=ci[0], ci_upper=ci[1],
        p_value=round(p_val, 6), t_statistic=round(t_stat, 3),
        n_observations=n, first_stage=first_stage_diag,
        true_late=true_late,
        estimation_error=round(err, 4) if err is not None else None,
    )


# ============================================================
# HAUSMAN ENDOGENEITY TEST
# ============================================================

def hausman_test(
    df: pd.DataFrame,
    outcome: str = "outcome",
    treatment: str = "actual_treatment",
    instrument: str = "assigned_treatment",
    covariates: Optional[List[str]] = None,
) -> HausmanResult:
    """
    Hausman test comparing OLS and IV estimates.

    H₀: D is exogenous (OLS is consistent and efficient)
    H₁: D is endogenous (only IV is consistent)

    Implementation via control function approach:
    1. Stage 1: D = π₀ + π₁Z + πX + v → get residuals v̂
    2. Augmented regression: Y = β₀ + τD + βX + ρv̂ + ε
    3. Test ρ = 0 (endogeneity test)
    """
    data = df.copy()
    Y = data[outcome].values
    D = data[treatment].values
    Z = data[instrument].values

    if covariates is None:
        covariates = ["age", "bmi", "pre_outcome"]
    available = [c for c in covariates if c in data.columns
                 and data[c].dtype in (np.float64, np.int64, float, int)]
    X_ctrl = data[available].values.astype(float) if available else np.empty((len(Y), 0))

    # Stage 1: D on Z + X → residuals
    X1 = np.column_stack([np.ones(len(Z)), Z, X_ctrl]) if X_ctrl.shape[1] > 0 else np.column_stack([np.ones(len(Z)), Z])
    stage1 = sm.OLS(D, X1).fit()
    v_hat = stage1.resid

    # OLS: Y on D + X
    X_ols = np.column_stack([np.ones(len(Y)), D, X_ctrl]) if X_ctrl.shape[1] > 0 else np.column_stack([np.ones(len(Y)), D])
    ols = sm.OLS(Y, X_ols).fit(cov_type="HC1")
    ols_est = ols.params[1]

    # Augmented: Y on D + X + v̂
    X_aug = np.column_stack([X_ols, v_hat])
    augmented = sm.OLS(Y, X_aug).fit(cov_type="HC1")
    rho = augmented.params[-1]
    rho_t = augmented.tvalues[-1]
    rho_p = augmented.pvalues[-1]

    # IV estimate for comparison
    iv_result = tsls_estimator(df, outcome, treatment, instrument, covariates)
    iv_est = iv_result.estimate

    endogenous = rho_p < 0.05

    return HausmanResult(
        ols_estimate=round(ols_est, 4),
        iv_estimate=iv_est,
        test_statistic=round(rho_t, 3),
        p_value=round(rho_p, 6),
        endogeneity_detected=endogenous,
        interpretation=("Endogeneity detected (p<0.05): IV preferred over OLS"
                        if endogenous else
                        "No endogeneity detected: OLS is efficient"),
    )


# ============================================================
# COMPLIANCE ANALYSIS
# ============================================================

def analyze_compliance(
    df: pd.DataFrame,
    assignment: str = "assigned_treatment",
    treatment: str = "actual_treatment",
) -> ComplianceAnalysis:
    """
    Estimate compliance type shares from observed data.

    Under monotonicity (no defiers):
    - P(always-taker) = P(D=1 | Z=0)
    - P(never-taker)  = P(D=0 | Z=1)
    - P(complier)     = 1 - P(AT) - P(NT)
    """
    Z = df[assignment].values
    D = df[treatment].values
    n = len(Z)

    # Observable compliance shares
    p_at = D[Z == 0].mean()        # Takes treatment despite assigned control
    p_nt = 1 - D[Z == 1].mean()   # Refuses treatment despite assigned treatment
    p_comp = 1 - p_at - p_nt
    p_comp = max(p_comp, 0)

    n_comp = int(round(n * p_comp))
    n_at = int(round(n * p_at))
    n_nt = int(round(n * p_nt))

    # Check if oracle compliance_type exists
    oracle = False
    oracle_acc = None
    if "compliance_type" in df.columns:
        oracle = True
        true_comp = (df["compliance_type"] == "complier").mean()
        oracle_acc = round(abs(p_comp - true_comp), 4)

    return ComplianceAnalysis(
        n_total=n, n_compliers_est=n_comp,
        n_always_takers_est=n_at, n_never_takers_est=n_nt,
        complier_share=round(p_comp, 4),
        always_taker_share=round(p_at, 4),
        never_taker_share=round(p_nt, 4),
        oracle_available=oracle, oracle_accuracy=oracle_acc,
    )


# ============================================================
# HELPERS
# ============================================================

def _compute_first_stage(
    df: pd.DataFrame,
    instrument: str,
    treatment: str,
    covariates: Optional[List[str]] = None,
) -> FirstStageDiagnostics:
    """Compute first-stage F-statistic and diagnostics."""
    Z = df[instrument].values
    D = df[treatment].values

    if covariates:
        available = [c for c in covariates if c in df.columns
                     and df[c].dtype in (np.float64, np.int64, float, int)]
        X_ctrl = df[available].values.astype(float)
        X = np.column_stack([np.ones(len(Z)), Z, X_ctrl])
    else:
        X = np.column_stack([np.ones(len(Z)), Z])

    model = sm.OLS(D, X).fit()

    # F-stat on excluded instrument (Z)
    coef_z = model.params[1]
    se_z = model.bse[1]
    t_z = model.tvalues[1]
    f_stat = t_z ** 2  # F = t² for single instrument

    # Partial R² of Z
    X_restricted = np.column_stack([np.ones(len(Z))] +
                                   ([X_ctrl] if covariates and len(available) > 0 else []))
    restricted = sm.OLS(D, X_restricted).fit()
    partial_r2 = 1 - model.ssr / restricted.ssr if restricted.ssr > 0 else 0

    compliance = D[Z == 1].mean() - D[Z == 0].mean()

    return FirstStageDiagnostics(
        f_statistic=round(f_stat, 2),
        f_p_value=round(1 - stats.f.cdf(f_stat, 1, len(Z) - X.shape[1]), 6),
        partial_r_squared=round(partial_r2, 4),
        instrument_coef=round(coef_z, 4),
        instrument_se=round(se_z, 4),
        instrument_t=round(t_z, 3),
        is_strong=f_stat > 10,
        compliance_rate=round(compliance, 4),
    )
