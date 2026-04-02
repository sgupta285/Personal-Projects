from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm

from did_lab.estimators import DidEstimate, twfe_did


@dataclass(slots=True)
class ParallelTrendsDiagnostic:
    slope_diff: float
    p_value: float
    passed: bool


@dataclass(slots=True)
class PlaceboDiagnostic:
    placebo_effect: float
    p_value: float


@dataclass(slots=True)
class PolicyEvaluationBundle:
    did: DidEstimate
    parallel_trends: ParallelTrendsDiagnostic
    placebo: PlaceboDiagnostic


def parallel_trends_test(
    frame: pd.DataFrame,
    outcome_col: str,
    unit_col: str,
    time_col: str,
    pre_period_count: int,
) -> ParallelTrendsDiagnostic:
    treatment_start = int(frame.loc[frame["ever_treated"] == 1, "treatment_cohort"].replace(-1, np.nan).dropna().min())
    pre = frame.loc[frame[time_col] < treatment_start].copy()
    if pre_period_count > 0:
        keep_periods = sorted(pre[time_col].unique())[-pre_period_count:]
        pre = pre.loc[pre[time_col].isin(keep_periods)].copy()
    pre["time_centered"] = pre[time_col] - pre[time_col].min()
    pre["interaction"] = pre["ever_treated"] * pre["time_centered"]
    model = sm.OLS(
        pre[outcome_col],
        sm.add_constant(pre[["ever_treated", "time_centered", "interaction", "covariate"]], has_constant="add"),
    ).fit(cov_type="cluster", cov_kwds={"groups": pre[unit_col]})
    slope_diff = float(model.params["interaction"])
    p_value = float(model.pvalues["interaction"])
    return ParallelTrendsDiagnostic(slope_diff=slope_diff, p_value=p_value, passed=bool(p_value >= 0.05))


def placebo_test(
    frame: pd.DataFrame,
    outcome_col: str,
    unit_col: str,
    time_col: str,
    cluster_col: str,
    shift: int,
) -> PlaceboDiagnostic:
    placebo = frame.copy()
    true_treatment_start = int(placebo.loc[placebo["ever_treated"] == 1, "treatment_cohort"].replace(-1, np.nan).dropna().min())
    placebo_start = max(placebo[time_col].min() + 2, true_treatment_start - shift)
    placebo = placebo.loc[placebo[time_col] < true_treatment_start].copy()
    placebo["post"] = (placebo[time_col] >= placebo_start).astype(int)
    estimate = twfe_did(placebo, outcome_col, unit_col, time_col, cluster_col)
    return PlaceboDiagnostic(placebo_effect=estimate.estimate, p_value=estimate.p_value)
