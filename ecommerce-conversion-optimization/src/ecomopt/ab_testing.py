from __future__ import annotations

import math
import pandas as pd
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_confint, proportions_ztest, proportion_effectsize


def summarize_experiment(cohorts: pd.DataFrame) -> pd.DataFrame:
    return (
        cohorts.groupby("variant")
        .agg(
            sessions=("session_id", "count"),
            conversions=("purchased", "sum"),
            conversion_rate=("purchased", "mean"),
            average_order_value=("order_value", lambda s: s[s > 0].mean() if (s > 0).any() else 0.0),
            revenue_per_session=("order_value", "mean"),
        )
        .reset_index()
    )


def minimum_detectable_effect(baseline_rate: float, n_per_group: int, alpha: float = 0.05, power: float = 0.8) -> float:
    solver = NormalIndPower()
    target_effect = solver.solve_power(nobs1=n_per_group, ratio=1.0, alpha=alpha, power=power)
    low, high = baseline_rate, min(0.999, baseline_rate + 0.25)
    for _ in range(80):
        mid = (low + high) / 2
        current = abs(proportion_effectsize(baseline_rate, mid))
        if current < target_effect:
            low = mid
        else:
            high = mid
    return high - baseline_rate


def compare_variants(cohorts: pd.DataFrame, alpha: float = 0.05) -> dict:
    summary = summarize_experiment(cohorts)
    control = summary.loc[summary["variant"] == "control"].iloc[0]
    treatment = summary.loc[summary["variant"] == "treatment"].iloc[0]

    count = [int(treatment["conversions"]), int(control["conversions"])]
    nobs = [int(treatment["sessions"]), int(control["sessions"])]
    stat, p_value = proportions_ztest(count=count, nobs=nobs)

    control_rate = float(control["conversion_rate"])
    treatment_rate = float(treatment["conversion_rate"])
    absolute_lift = treatment_rate - control_rate
    relative_lift = treatment_rate / control_rate - 1 if control_rate > 0 else math.nan
    ci_control = proportion_confint(int(control["conversions"]), int(control["sessions"]), alpha=alpha, method="wilson")
    ci_treat = proportion_confint(int(treatment["conversions"]), int(treatment["sessions"]), alpha=alpha, method="wilson")
    se = math.sqrt(max(control_rate * (1 - control_rate) / control["sessions"] + treatment_rate * (1 - treatment_rate) / treatment["sessions"], 1e-12))
    lift_ci = (absolute_lift - 1.96 * se, absolute_lift + 1.96 * se)
    effect_size = proportion_effectsize(control_rate, treatment_rate)
    observed_power = NormalIndPower().power(effect_size=effect_size, nobs1=int(control["sessions"]), ratio=treatment["sessions"] / control["sessions"], alpha=alpha)
    mde = minimum_detectable_effect(control_rate, int(control["sessions"]), alpha=alpha, power=0.8)
    return {
        "control_sessions": int(control["sessions"]),
        "treatment_sessions": int(treatment["sessions"]),
        "control_conversion_rate": round(control_rate, 6),
        "treatment_conversion_rate": round(treatment_rate, 6),
        "absolute_lift": round(absolute_lift, 6),
        "relative_lift": round(relative_lift, 6),
        "z_stat": round(float(stat), 6),
        "p_value": round(float(p_value), 6),
        "control_ci": [round(float(ci_control[0]), 6), round(float(ci_control[1]), 6)],
        "treatment_ci": [round(float(ci_treat[0]), 6), round(float(ci_treat[1]), 6)],
        "lift_ci": [round(float(lift_ci[0]), 6), round(float(lift_ci[1]), 6)],
        "observed_power": round(float(observed_power), 6),
        "mde_at_80_power": round(float(mde), 6),
    }


def segment_lift_table(cohorts: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    grouped = (
        cohorts.groupby(group_cols + ["variant"])
        .agg(sessions=("session_id", "count"), conversions=("purchased", "sum"), purchase_rate=("purchased", "mean"))
        .reset_index()
    )
    pivot = grouped.pivot_table(index=group_cols, columns="variant", values=["sessions", "conversions", "purchase_rate"], fill_value=0)
    pivot.columns = [f"{metric}_{variant}" for metric, variant in pivot.columns]
    pivot = pivot.reset_index()
    pivot["absolute_lift"] = pivot["purchase_rate_treatment"] - pivot["purchase_rate_control"]
    pivot["relative_lift"] = pivot["purchase_rate_treatment"] / pivot["purchase_rate_control"] - 1
    pivot = pivot.replace([float("inf"), float("-inf")], 0)
    return pivot.sort_values("absolute_lift", ascending=False)
