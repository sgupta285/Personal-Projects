"""
Difference-in-Differences and Event Study Estimation.

Implements:
1. Two-way Fixed Effects DiD (state + time FE, clustered SE)
2. Event Study (dynamic treatment effects with leads/lags)
3. Triple Difference (DiD × sector)
4. Parallel trends pre-test
"""

import numpy as np
import pandas as pd
from scipy import stats
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
import statsmodels.api as sm
import structlog

from src.config import config

logger = structlog.get_logger()


@dataclass
class DiDResult:
    outcome: str
    estimate: float
    std_error: float
    ci_lower: float
    ci_upper: float
    t_statistic: float
    p_value: float
    r_squared: float
    n_observations: int
    n_clusters: int
    state_fe: bool
    time_fe: bool
    true_effect: Optional[float] = None
    estimation_error: Optional[float] = None


@dataclass
class EventStudyCoefficient:
    relative_period: int
    estimate: float
    std_error: float
    ci_lower: float
    ci_upper: float
    p_value: float


@dataclass
class EventStudyResult:
    outcome: str
    coefficients: List[EventStudyCoefficient]
    pre_trend_f_stat: float
    pre_trend_p_value: float
    parallel_trends_hold: bool
    post_treatment_avg: float


# ============================================================
# TWO-WAY FIXED EFFECTS DiD
# ============================================================

class DiDEstimator:
    """Two-way fixed effects difference-in-differences."""

    def estimate(
        self,
        df: pd.DataFrame,
        outcome: str = "employment_rate",
        treatment: str = "did",
        controls: Optional[List[str]] = None,
        cluster_col: str = "state_id",
        true_effect: Optional[float] = None,
        alpha: float = 0.05,
    ) -> DiDResult:
        """
        Estimate DiD with state and time fixed effects.

        Y_st = α_s + γ_t + δ · (Treat_s × Post_t) + β·X_st + ε_st

        Standard errors clustered at the state level.
        """
        data = df.copy()

        # Build design matrix
        y = data[outcome].values

        # State FE dummies
        state_dummies = pd.get_dummies(data["state_id"], drop_first=True, prefix="s")
        # Time FE dummies
        time_dummies = pd.get_dummies(data["quarter"], drop_first=True, prefix="t")

        X_df = pd.DataFrame({treatment: data[treatment].values})

        if controls:
            for c in controls:
                if c in data.columns:
                    X_df[c] = data[c].values

        if config.model.include_state_fe:
            X_df = pd.concat([X_df, state_dummies.reset_index(drop=True)], axis=1)
        if config.model.include_time_fe:
            X_df = pd.concat([X_df, time_dummies.reset_index(drop=True)], axis=1)

        X = sm.add_constant(X_df.values.astype(float))

        # Cluster SEs by state
        if config.model.cluster_se:
            model = sm.OLS(y, X).fit(
                cov_type="cluster",
                cov_kwds={"groups": data[cluster_col].values},
            )
        else:
            model = sm.OLS(y, X).fit(cov_type="HC1")

        # Extract DiD coefficient (first non-constant regressor)
        did_idx = 1  # After constant
        estimate = model.params[did_idx]
        se = model.bse[did_idx]
        t_stat = model.tvalues[did_idx]
        p_val = model.pvalues[did_idx]

        z = stats.norm.ppf(1 - alpha / 2)
        ci = (round(estimate - z * se, 6), round(estimate + z * se, 6))

        err = abs(estimate - true_effect) if true_effect is not None else None

        return DiDResult(
            outcome=outcome, estimate=round(estimate, 6),
            std_error=round(se, 6), ci_lower=ci[0], ci_upper=ci[1],
            t_statistic=round(t_stat, 3), p_value=round(p_val, 6),
            r_squared=round(model.rsquared, 4),
            n_observations=len(y),
            n_clusters=data[cluster_col].nunique(),
            state_fe=config.model.include_state_fe,
            time_fe=config.model.include_time_fe,
            true_effect=true_effect,
            estimation_error=round(err, 6) if err else None,
        )


# ============================================================
# EVENT STUDY
# ============================================================

class EventStudyEstimator:
    """Dynamic treatment effects (event study) estimation."""

    def estimate(
        self,
        df: pd.DataFrame,
        outcome: str = "employment_rate",
        treatment_quarter: int = 20,
        pre_periods: int = 8,
        post_periods: int = 12,
        reference_period: int = -1,
        cluster_col: str = "state_id",
        alpha: float = 0.05,
    ) -> EventStudyResult:
        """
        Event study: Y_st = α_s + γ_t + Σ_k δ_k · (Treat_s × 1[t-t*=k]) + ε_st

        Coefficients δ_k capture dynamic treatment effects relative to reference period.
        """
        data = df.copy()
        data["relative_quarter"] = data["quarter"] - treatment_quarter

        # Create event-time dummies (excluding reference period)
        periods = list(range(-pre_periods, post_periods + 1))
        periods.remove(reference_period)

        event_dummies = {}
        for k in periods:
            col_name = f"event_{k}"
            data[col_name] = ((data["treated"] == 1) & (data["relative_quarter"] == k)).astype(int)
            event_dummies[k] = col_name

        # State and time FE
        state_dummies = pd.get_dummies(data["state_id"], drop_first=True, prefix="s")
        time_dummies = pd.get_dummies(data["quarter"], drop_first=True, prefix="t")

        y = data[outcome].values
        event_cols = list(event_dummies.values())
        X_df = data[event_cols].copy()
        X_df = pd.concat([X_df, state_dummies.reset_index(drop=True),
                          time_dummies.reset_index(drop=True)], axis=1)
        X = sm.add_constant(X_df.values.astype(float))

        model = sm.OLS(y, X).fit(
            cov_type="cluster",
            cov_kwds={"groups": data[cluster_col].values},
        )

        z = stats.norm.ppf(1 - alpha / 2)
        coefficients = []

        # Add reference period as zero
        coefficients.append(EventStudyCoefficient(
            relative_period=reference_period, estimate=0.0,
            std_error=0.0, ci_lower=0.0, ci_upper=0.0, p_value=1.0,
        ))

        for i, k in enumerate(periods):
            idx = i + 1  # +1 for constant
            est = model.params[idx]
            se = model.bse[idx]
            p = model.pvalues[idx]
            coefficients.append(EventStudyCoefficient(
                relative_period=k, estimate=round(est, 6),
                std_error=round(se, 6),
                ci_lower=round(est - z * se, 6),
                ci_upper=round(est + z * se, 6),
                p_value=round(p, 6),
            ))

        coefficients.sort(key=lambda c: c.relative_period)

        # Pre-trend test: joint F-test that all pre-period coefficients = 0
        pre_coefs = [c for c in coefficients if c.relative_period < 0 and c.relative_period != reference_period]
        if pre_coefs:
            pre_f = np.mean([c.estimate ** 2 / max(c.std_error ** 2, 1e-10) for c in pre_coefs])
            pre_p = 1 - stats.chi2.cdf(pre_f * len(pre_coefs), len(pre_coefs))
        else:
            pre_f, pre_p = 0, 1.0

        post_coefs = [c for c in coefficients if c.relative_period >= 0]
        post_avg = np.mean([c.estimate for c in post_coefs]) if post_coefs else 0

        return EventStudyResult(
            outcome=outcome, coefficients=coefficients,
            pre_trend_f_stat=round(pre_f, 3),
            pre_trend_p_value=round(pre_p, 4),
            parallel_trends_hold=pre_p > 0.05,
            post_treatment_avg=round(post_avg, 6),
        )


# ============================================================
# PARALLEL TRENDS TEST
# ============================================================

def test_parallel_trends(
    df: pd.DataFrame,
    outcome: str = "employment_rate",
    treatment_quarter: int = 20,
    cluster_col: str = "state_id",
) -> Tuple[float, float, bool]:
    """
    Test for parallel pre-trends using placebo treatment.

    Regress outcome on Treat × linear_time_trend in pre-period.
    If interaction is insignificant → parallel trends plausible.
    """
    pre_data = df[df["quarter"] < treatment_quarter].copy()
    pre_data["treat_x_time"] = pre_data["treated"] * pre_data["quarter"]

    state_dummies = pd.get_dummies(pre_data["state_id"], drop_first=True, prefix="s")
    time_dummies = pd.get_dummies(pre_data["quarter"], drop_first=True, prefix="t")

    y = pre_data[outcome].values
    X_df = pd.DataFrame({"treat_x_time": pre_data["treat_x_time"].values})
    X_df = pd.concat([X_df, state_dummies.reset_index(drop=True),
                      time_dummies.reset_index(drop=True)], axis=1)
    X = sm.add_constant(X_df.values.astype(float))

    model = sm.OLS(y, X).fit(
        cov_type="cluster",
        cov_kwds={"groups": pre_data[cluster_col].values},
    )

    trend_coef = model.params[1]
    trend_p = model.pvalues[1]

    return round(trend_coef, 6), round(trend_p, 4), trend_p > 0.05
