from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.optimize import minimize


@dataclass(slots=True)
class DidEstimate:
    term: str
    estimate: float
    std_error: float
    p_value: float
    ci_low: float
    ci_high: float
    n_obs: int


@dataclass(slots=True)
class EventStudyEstimate:
    estimates: pd.DataFrame
    joint_pretrend_p_value: float | None


@dataclass(slots=True)
class SyntheticControlEstimate:
    treated_unit: str
    donor_weights: pd.Series
    avg_gap_post: float
    pre_rmse: float
    trajectory: pd.DataFrame


@dataclass(slots=True)
class FittedModel:
    model: object
    design_columns: list[str]


def _fit_ols(df: pd.DataFrame, y_col: str, x_cols: Sequence[str], cluster_col: str | None = None):
    X = sm.add_constant(df[list(x_cols)], has_constant="add")
    y = df[y_col]
    model = sm.OLS(y, X)
    if cluster_col:
        fitted = model.fit(cov_type="cluster", cov_kwds={"groups": df[cluster_col]})
    else:
        fitted = model.fit()
    return fitted


def twfe_did(
    frame: pd.DataFrame,
    outcome_col: str,
    unit_col: str,
    time_col: str,
    cluster_col: str,
) -> DidEstimate:
    design = frame[[outcome_col, unit_col, time_col, "ever_treated", "post"]].copy()
    design["did_term"] = design["ever_treated"] * design["post"]
    unit_dummies = pd.get_dummies(design[unit_col], prefix="unit", drop_first=True, dtype=float)
    time_dummies = pd.get_dummies(design[time_col], prefix="time", drop_first=True, dtype=float)
    X = pd.concat([design[["did_term"]].astype(float), unit_dummies, time_dummies], axis=1)
    fitted = _fit_ols(pd.concat([design[[outcome_col, cluster_col]], X], axis=1), outcome_col, X.columns.tolist(), cluster_col)
    estimate = float(fitted.params["did_term"])
    se = float(fitted.bse["did_term"])
    ci_low, ci_high = fitted.conf_int().loc["did_term"].tolist()
    return DidEstimate(
        term="did_term",
        estimate=estimate,
        std_error=se,
        p_value=float(fitted.pvalues["did_term"]),
        ci_low=float(ci_low),
        ci_high=float(ci_high),
        n_obs=int(frame.shape[0]),
    )


def event_study(
    frame: pd.DataFrame,
    outcome_col: str,
    unit_col: str,
    time_col: str,
    cluster_col: str,
    min_event: int = -6,
    max_event: int = 6,
    reference_period: int = -1,
) -> EventStudyEstimate:
    design = frame.copy()
    design = design[design["ever_treated"].eq(1) | design["ever_treated"].eq(0)].copy()
    design["event_time"] = design["time_id"] - design["treatment_cohort"].where(design["treatment_cohort"] >= 0, np.nan)
    design["event_time"] = design["event_time"].fillna(0)

    event_terms = []
    for rel_time in range(min_event, max_event + 1):
        if rel_time == reference_period:
            continue
        col = f"event_{rel_time:+d}".replace("+", "p").replace("-", "m")
        design[col] = ((design["event_time"] == rel_time) & (design["ever_treated"] == 1)).astype(float)
        event_terms.append((rel_time, col))

    unit_dummies = pd.get_dummies(design[unit_col], prefix="unit", drop_first=True, dtype=float)
    time_dummies = pd.get_dummies(design[time_col], prefix="time", drop_first=True, dtype=float)
    X = pd.concat([design[[col for _, col in event_terms]], unit_dummies, time_dummies], axis=1)
    fitted = _fit_ols(pd.concat([design[[outcome_col, cluster_col]], X], axis=1), outcome_col, X.columns.tolist(), cluster_col)

    rows = []
    pre_cols = []
    for rel_time, col in event_terms:
        if col not in fitted.params:
            continue
        ci_low, ci_high = fitted.conf_int().loc[col].tolist()
        rows.append(
            {
                "event_time": rel_time,
                "estimate": float(fitted.params[col]),
                "std_error": float(fitted.bse[col]),
                "p_value": float(fitted.pvalues[col]),
                "ci_low": float(ci_low),
                "ci_high": float(ci_high),
            }
        )
        if rel_time < 0:
            pre_cols.append(col)

    p_value = None
    if pre_cols:
        restriction = np.zeros((len(pre_cols), len(fitted.params)))
        param_names = list(fitted.params.index)
        for idx, col in enumerate(pre_cols):
            restriction[idx, param_names.index(col)] = 1.0
        wald = fitted.wald_test(restriction, scalar=True)
        p_value = float(np.asarray(wald.pvalue).item())

    estimates = pd.DataFrame(rows).sort_values("event_time").reset_index(drop=True)
    return EventStudyEstimate(estimates=estimates, joint_pretrend_p_value=p_value)


def synthetic_control(
    frame: pd.DataFrame,
    outcome_col: str,
    unit_col: str,
    time_col: str,
    treatment_start: int,
    treated_unit: str | None = None,
) -> SyntheticControlEstimate:
    donor_frame = frame.copy()
    treated_candidates = sorted(donor_frame.loc[donor_frame["ever_treated"] == 1, unit_col].unique())
    if not treated_candidates:
        raise ValueError("Synthetic control requires at least one treated unit.")
    target_unit = treated_unit or treated_candidates[0]
    controls = sorted(donor_frame.loc[donor_frame["ever_treated"] == 0, unit_col].unique())
    if not controls:
        raise ValueError("Synthetic control requires at least one donor unit.")

    pivot = donor_frame.pivot(index=time_col, columns=unit_col, values=outcome_col).sort_index()
    pre = pivot.loc[pivot.index < treatment_start]
    post = pivot.loc[pivot.index >= treatment_start]

    y_treated_pre = pre[target_unit].to_numpy()
    X_pre = pre[controls].to_numpy()

    n_controls = len(controls)

    def objective(weights: np.ndarray) -> float:
        residual = y_treated_pre - X_pre @ weights
        return float(np.mean(residual ** 2))

    cons = ({"type": "eq", "fun": lambda w: np.sum(w) - 1.0},)
    bounds = [(0.0, 1.0) for _ in range(n_controls)]
    init = np.repeat(1.0 / n_controls, n_controls)
    result = minimize(objective, init, method="SLSQP", bounds=bounds, constraints=cons)
    if not result.success:
        raise RuntimeError(f"Synthetic control optimization failed: {result.message}")

    weights = pd.Series(result.x, index=controls, name="weight")
    synthetic_series = pivot[controls].to_numpy() @ result.x
    trajectory = pd.DataFrame(
        {
            time_col: pivot.index,
            "treated_actual": pivot[target_unit].to_numpy(),
            "synthetic_control": synthetic_series,
        }
    )
    trajectory["gap"] = trajectory["treated_actual"] - trajectory["synthetic_control"]
    pre_rmse = float(np.sqrt(np.mean((trajectory.loc[trajectory[time_col] < treatment_start, "gap"]) ** 2)))
    avg_gap_post = float(trajectory.loc[trajectory[time_col] >= treatment_start, "gap"].mean())
    return SyntheticControlEstimate(
        treated_unit=target_unit,
        donor_weights=weights.sort_values(ascending=False),
        avg_gap_post=avg_gap_post,
        pre_rmse=pre_rmse,
        trajectory=trajectory,
    )
