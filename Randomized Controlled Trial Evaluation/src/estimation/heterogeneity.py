"""
Heterogeneous Treatment Effect Estimation.

Implements:
1. Subgroup CATE — difference-in-means within strata
2. Interaction Regression — fully interacted OLS for CATE
3. Causal Forest (simplified honest splitting) — tree-based CATE
4. GATES (Group Average Treatment Effects) — sorted group analysis
5. BLP (Best Linear Predictor) — omnibus heterogeneity test
6. CLAN (Characteristics of most/least affected) — profiling
"""

import numpy as np
import pandas as pd
from scipy import stats
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestRegressor
import statsmodels.api as sm
import structlog

logger = structlog.get_logger()


@dataclass
class CATEResult:
    subgroup: str
    subgroup_value: str
    estimate: float
    std_error: float
    ci_lower: float
    ci_upper: float
    p_value: float
    n_obs: int
    n_treated: int
    n_control: int
    true_cate: Optional[float] = None
    estimation_error: Optional[float] = None


@dataclass
class InteractionResult:
    """Result from fully interacted regression."""
    base_ate: float
    base_se: float
    interactions: Dict[str, float]       # covariate → interaction coefficient
    interaction_ses: Dict[str, float]
    interaction_pvals: Dict[str, float]
    significant_moderators: List[str]
    r_squared: float
    n_obs: int


@dataclass
class CausalForestResult:
    """Result from causal forest CATE estimation."""
    cate_predictions: np.ndarray      # Individual-level τ̂(x)
    feature_importances: Dict[str, float]
    ate_estimate: float               # Average of τ̂(x)
    cate_std: float                   # Heterogeneity = std(τ̂(x))
    cate_iqr: Tuple[float, float]     # IQR of τ̂(x)


@dataclass
class GATESResult:
    """Group Average Treatment Effects (Chernozhukov et al. 2018)."""
    group_estimates: List[float]       # GATE for each quintile
    group_ses: List[float]
    group_sizes: List[int]
    heterogeneity_p: float             # Test: all groups equal?
    most_affected_profile: Dict        # Characteristics of top quintile
    least_affected_profile: Dict       # Characteristics of bottom quintile


@dataclass
class BLPResult:
    """Best Linear Predictor test for heterogeneity."""
    beta_1: float                      # Loading on τ̂(x): β₁=1 if CATE well-calibrated
    beta_1_se: float
    beta_1_p: float
    heterogeneity_detected: bool       # β₁ significantly > 0


# ============================================================
# SUBGROUP CATE
# ============================================================

def estimate_cate_subgroup(
    df: pd.DataFrame,
    outcome: str = "outcome",
    treatment: str = "assigned_treatment",
    subgroup_col: str = "age_group",
    true_cate: Optional[Dict[str, float]] = None,
    alpha: float = 0.05,
) -> List[CATEResult]:
    """Estimate CATE via difference-in-means within each subgroup."""
    results = []
    z = stats.norm.ppf(1 - alpha / 2)

    for val in sorted(df[subgroup_col].unique()):
        sub = df[df[subgroup_col] == val]
        treat = sub[sub[treatment] == 1][outcome].values
        ctrl = sub[sub[treatment] == 0][outcome].values

        if len(treat) < 20 or len(ctrl) < 20:
            continue

        cate = treat.mean() - ctrl.mean()
        se = np.sqrt(np.var(treat, ddof=1) / len(treat) + np.var(ctrl, ddof=1) / len(ctrl))
        t_stat = cate / se if se > 0 else 0
        p_val = 2 * (1 - stats.norm.cdf(abs(t_stat)))

        true_val = true_cate.get(str(val)) if true_cate else None
        err = abs(cate - true_val) if true_val is not None else None

        results.append(CATEResult(
            subgroup=subgroup_col, subgroup_value=str(val),
            estimate=round(cate, 4), std_error=round(se, 4),
            ci_lower=round(cate - z * se, 4),
            ci_upper=round(cate + z * se, 4),
            p_value=round(p_val, 6),
            n_obs=len(sub), n_treated=len(treat), n_control=len(ctrl),
            true_cate=round(true_val, 4) if true_val is not None else None,
            estimation_error=round(err, 4) if err is not None else None,
        ))

    return results


# ============================================================
# INTERACTION REGRESSION
# ============================================================

def interaction_regression(
    df: pd.DataFrame,
    outcome: str = "outcome",
    treatment: str = "assigned_treatment",
    moderators: Optional[List[str]] = None,
    alpha: float = 0.05,
) -> InteractionResult:
    """
    Fully interacted regression for effect heterogeneity.

    Y = β₀ + τT + Σ γ_k X_k + Σ δ_k (T × X_k) + ε

    δ_k measures how the treatment effect varies with moderator X_k.
    Significant δ_k → X_k is a treatment effect modifier.
    """
    data = df.copy()
    if moderators is None:
        moderators = ["age", "bmi", "pre_outcome", "biomarker_a", "biomarker_b"]

    available = [m for m in moderators if m in data.columns
                 and data[m].dtype in (np.float64, np.int64, float, int)]

    T = data[treatment].values.astype(float)
    Y = data[outcome].values

    # Center moderators
    X_raw = data[available].values.astype(float)
    X_centered = X_raw - X_raw.mean(axis=0)

    # Design: [1, T, X_centered, T*X_centered]
    interactions = T[:, None] * X_centered
    X_design = np.column_stack([np.ones(len(T)), T, X_centered, interactions])

    model = sm.OLS(Y, X_design).fit(cov_type="HC2")

    base_ate = model.params[1]
    base_se = model.bse[1]

    # Interaction coefficients start after 1 + 1 + len(available)
    int_start = 2 + len(available)
    interaction_coefs = {}
    interaction_ses = {}
    interaction_pvals = {}
    significant = []

    for i, mod in enumerate(available):
        idx = int_start + i
        interaction_coefs[mod] = round(model.params[idx], 4)
        interaction_ses[mod] = round(model.bse[idx], 4)
        interaction_pvals[mod] = round(model.pvalues[idx], 6)
        if model.pvalues[idx] < alpha:
            significant.append(mod)

    return InteractionResult(
        base_ate=round(base_ate, 4), base_se=round(base_se, 4),
        interactions=interaction_coefs,
        interaction_ses=interaction_ses,
        interaction_pvals=interaction_pvals,
        significant_moderators=significant,
        r_squared=round(model.rsquared, 4),
        n_obs=len(Y),
    )


# ============================================================
# CAUSAL FOREST (SIMPLIFIED)
# ============================================================

class CausalForestEstimator:
    """
    Simplified causal forest for individual-level CATE estimation.

    Uses the T-learner approach with honest splitting:
    - Fit μ₁(x) = E[Y|T=1, X=x] on treatment group
    - Fit μ₀(x) = E[Y|T=0, X=x] on control group
    - τ̂(x) = μ̂₁(x) - μ̂₀(x)

    Cross-fitting (2-fold) to avoid overfitting in CATE estimates.
    """

    def __init__(self, n_trees: int = 500, min_samples_leaf: int = 50, seed: int = 42):
        self.n_trees = n_trees
        self.min_leaf = min_samples_leaf
        self.seed = seed

    def estimate(
        self,
        df: pd.DataFrame,
        outcome: str = "outcome",
        treatment: str = "assigned_treatment",
        features: Optional[List[str]] = None,
    ) -> CausalForestResult:
        """Estimate individual CATEs via T-learner with cross-fitting."""
        data = df.copy()
        if features is None:
            features = ["age", "bmi", "pre_outcome", "biomarker_a", "biomarker_b"]
        available = [f for f in features if f in data.columns
                     and data[f].dtype in (np.float64, np.int64, float, int)]

        X = data[available].values.astype(float)
        Y = data[outcome].values
        T = data[treatment].values
        n = len(Y)

        # Cross-fitting: 2-fold
        cate_hat = np.zeros(n)
        kf = KFold(n_splits=2, shuffle=True, random_state=self.seed)

        feature_imp_accum = np.zeros(len(available))

        for train_idx, eval_idx in kf.split(X):
            X_train, X_eval = X[train_idx], X[eval_idx]
            Y_train, T_train = Y[train_idx], T[train_idx]

            # Fit μ₁(x) on treated in training fold
            treat_mask = T_train == 1
            rf1 = RandomForestRegressor(
                n_estimators=self.n_trees, min_samples_leaf=self.min_leaf,
                random_state=self.seed, n_jobs=-1,
            )
            rf1.fit(X_train[treat_mask], Y_train[treat_mask])

            # Fit μ₀(x) on control in training fold
            ctrl_mask = T_train == 0
            rf0 = RandomForestRegressor(
                n_estimators=self.n_trees, min_samples_leaf=self.min_leaf,
                random_state=self.seed, n_jobs=-1,
            )
            rf0.fit(X_train[ctrl_mask], Y_train[ctrl_mask])

            # Predict on evaluation fold
            cate_hat[eval_idx] = rf1.predict(X_eval) - rf0.predict(X_eval)

            # Feature importance (average across both models)
            feature_imp_accum += (rf1.feature_importances_ + rf0.feature_importances_) / 2

        feature_imp_accum /= 2  # Average across folds
        feat_imp = {f: round(imp, 4) for f, imp in zip(available, feature_imp_accum)}
        feat_imp = dict(sorted(feat_imp.items(), key=lambda x: x[1], reverse=True))

        return CausalForestResult(
            cate_predictions=np.round(cate_hat, 4),
            feature_importances=feat_imp,
            ate_estimate=round(cate_hat.mean(), 4),
            cate_std=round(cate_hat.std(), 4),
            cate_iqr=(round(np.percentile(cate_hat, 25), 4),
                      round(np.percentile(cate_hat, 75), 4)),
        )


# ============================================================
# GATES (GROUP AVERAGE TREATMENT EFFECTS)
# ============================================================

def estimate_gates(
    df: pd.DataFrame,
    cate_predictions: np.ndarray,
    outcome: str = "outcome",
    treatment: str = "assigned_treatment",
    n_groups: int = 5,
    alpha: float = 0.05,
) -> GATESResult:
    """
    GATES: Sort subjects by predicted CATE, form quintiles,
    estimate group-specific ATEs.

    Tests omnibus hypothesis: H₀ all groups have equal treatment effect.
    Profiles most/least affected groups (CLAN).
    """
    data = df.copy()
    data["cate_hat"] = cate_predictions
    data["cate_group"] = pd.qcut(data["cate_hat"], n_groups, labels=False)

    group_ests = []
    group_ses = []
    group_sizes = []

    for g in range(n_groups):
        grp = data[data["cate_group"] == g]
        treat = grp[grp[treatment] == 1][outcome].values
        ctrl = grp[grp[treatment] == 0][outcome].values

        if len(treat) < 10 or len(ctrl) < 10:
            group_ests.append(0)
            group_ses.append(999)
            group_sizes.append(len(grp))
            continue

        gate = treat.mean() - ctrl.mean()
        se = np.sqrt(np.var(treat, ddof=1) / len(treat) + np.var(ctrl, ddof=1) / len(ctrl))
        group_ests.append(round(gate, 4))
        group_ses.append(round(se, 4))
        group_sizes.append(len(grp))

    # Omnibus test: F-test that all group effects are equal
    if len([s for s in group_ses if s < 100]) >= 2:
        overall_var = np.var(group_ests)
        within_var = np.mean([s ** 2 for s in group_ses if s < 100])
        f_stat = overall_var / max(within_var, 1e-10)
        het_p = 1 - stats.f.cdf(f_stat, n_groups - 1, sum(group_sizes) - n_groups)
    else:
        het_p = 1.0

    # CLAN: profile most and least affected
    profile_cols = ["age", "bmi", "severity", "gender", "biomarker_a", "biomarker_b"]
    available_profile = [c for c in profile_cols if c in data.columns]

    top_group = data[data["cate_group"] == n_groups - 1]
    bottom_group = data[data["cate_group"] == 0]

    most_affected = {}
    least_affected = {}
    for col in available_profile:
        if data[col].dtype in (np.float64, np.int64, float, int):
            most_affected[col] = round(top_group[col].mean(), 2)
            least_affected[col] = round(bottom_group[col].mean(), 2)
        else:
            most_affected[col] = top_group[col].mode().iloc[0] if len(top_group) > 0 else "N/A"
            least_affected[col] = bottom_group[col].mode().iloc[0] if len(bottom_group) > 0 else "N/A"

    return GATESResult(
        group_estimates=group_ests, group_ses=group_ses,
        group_sizes=group_sizes, heterogeneity_p=round(het_p, 6),
        most_affected_profile=most_affected,
        least_affected_profile=least_affected,
    )


# ============================================================
# BLP (BEST LINEAR PREDICTOR) HETEROGENEITY TEST
# ============================================================

def blp_test(
    df: pd.DataFrame,
    cate_predictions: np.ndarray,
    outcome: str = "outcome",
    treatment: str = "assigned_treatment",
) -> BLPResult:
    """
    Best Linear Predictor test (Chernozhukov et al. 2018).

    Y = β₀ + β₁·(T - p(Z))·(τ̂(X) - τ̄) + controls + ε

    β₁ > 0 and significant → heterogeneity exists and τ̂ captures it.
    β₁ ≈ 1 → CATE model is well-calibrated.
    """
    data = df.copy()
    Y = data[outcome].values
    T = data[treatment].values.astype(float)
    tau_hat = cate_predictions
    tau_bar = tau_hat.mean()

    # Treatment propensity (known 0.5 in RCT)
    p = T.mean()

    # Interaction term: (T - p) × (τ̂ - τ̄)
    interaction = (T - p) * (tau_hat - tau_bar)

    # Regression: Y on constant + (T-p) + interaction
    X = np.column_stack([np.ones(len(Y)), T - p, interaction])
    model = sm.OLS(Y, X).fit(cov_type="HC2")

    beta_1 = model.params[2]
    beta_1_se = model.bse[2]
    beta_1_p = model.pvalues[2]

    return BLPResult(
        beta_1=round(beta_1, 4),
        beta_1_se=round(beta_1_se, 4),
        beta_1_p=round(beta_1_p, 6),
        heterogeneity_detected=beta_1_p < 0.05,
    )
