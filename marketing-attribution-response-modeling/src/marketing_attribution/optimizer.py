from __future__ import annotations

from dataclasses import dataclass
import math

import pandas as pd

from marketing_attribution.response import response_function


@dataclass(slots=True)
class BudgetResult:
    allocations: pd.DataFrame
    total_budget: float
    estimated_conversion_lift: float
    estimated_revenue_lift: float


def _marginal(row: pd.Series, spend: float) -> float:
    alpha = float(row["alpha"])
    beta = float(row["beta"])
    return alpha * beta * math.exp(-beta * spend)


def optimize_budget(curves: pd.DataFrame, step: float = 250.0) -> BudgetResult:
    work = curves.copy().set_index("channel")
    work["current_spend"] = work["recent_avg_spend"].round(2)
    work["recommended_spend"] = work["current_spend"]
    work["min_spend"] = work["current_spend"] * 0.60
    work["max_spend"] = work["current_spend"] * 1.40
    total_budget = float(work["current_spend"].sum())

    for _ in range(250):
        donor_scores = []
        receiver_scores = []
        for channel, row in work.iterrows():
            spend = float(row["recommended_spend"])
            if spend - step >= float(row["min_spend"]):
                donor_scores.append((channel, _marginal(row, spend - step / 2)))
            if spend + step <= float(row["max_spend"]):
                receiver_scores.append((channel, _marginal(row, spend + step / 2)))
        if not donor_scores or not receiver_scores:
            break
        donor = min(donor_scores, key=lambda item: item[1])
        receiver = max(receiver_scores, key=lambda item: item[1])
        if donor[0] == receiver[0] or receiver[1] <= donor[1]:
            break
        work.loc[donor[0], "recommended_spend"] -= step
        work.loc[receiver[0], "recommended_spend"] += step

    work["current_estimated_conversions"] = work.apply(lambda row: response_function(row["current_spend"], row["alpha"], row["beta"]), axis=1)
    work["recommended_estimated_conversions"] = work.apply(lambda row: response_function(row["recommended_spend"], row["alpha"], row["beta"]), axis=1)
    work["current_estimated_revenue"] = work["current_estimated_conversions"] * work["aov"]
    work["recommended_estimated_revenue"] = work["recommended_estimated_conversions"] * work["aov"]
    work["spend_delta"] = work["recommended_spend"] - work["current_spend"]
    work["conversion_delta"] = work["recommended_estimated_conversions"] - work["current_estimated_conversions"]
    work["revenue_delta"] = work["recommended_estimated_revenue"] - work["current_estimated_revenue"]

    allocation_df = work.reset_index().sort_values("conversion_delta", ascending=False).reset_index(drop=True)
    conv_lift = float(allocation_df["conversion_delta"].sum())
    rev_lift = float(allocation_df["revenue_delta"].sum())
    return BudgetResult(
        allocations=allocation_df,
        total_budget=total_budget,
        estimated_conversion_lift=conv_lift,
        estimated_revenue_lift=rev_lift,
    )
