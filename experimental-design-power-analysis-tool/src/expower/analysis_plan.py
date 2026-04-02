from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class AnalysisPlan:
    design_type: str
    outcome_type: str
    estimand: str
    statistical_test: str
    adjustment_recommendation: str
    randomization_recommendation: str
    notes: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def recommend_analysis_plan(
    design_type: str,
    outcome_type: str,
    covariates_available: bool = True,
    clustering_present: bool = False,
) -> AnalysisPlan:
    if design_type == "between_subjects" and outcome_type == "continuous":
        test = "Two-sample t-test with OLS confirmation"
        estimand = "Average treatment effect on the outcome mean"
    elif design_type == "between_subjects" and outcome_type == "binary":
        test = "Difference in proportions with logistic regression confirmation"
        estimand = "Average treatment effect on conversion probability"
    elif design_type == "within_subjects":
        test = "Paired t-test with mixed-effects sensitivity analysis"
        estimand = "Average within-subject treatment effect"
    elif design_type == "clustered":
        test = "Cluster-robust OLS or mixed-effects model"
        estimand = "Average treatment effect accounting for cluster assignment"
    else:
        raise ValueError("Unsupported design_type or outcome_type")

    adjustment = (
        "Use CUPED or ANCOVA adjustment if high-quality pre-period covariates are available."
        if covariates_available
        else "Primary analysis can remain unadjusted. Keep a prespecified covariate-free estimate."
    )
    randomization = (
        "Use blocked randomization on pre-period risk or geography to stabilize balance."
        if design_type == "between_subjects"
        else "Keep assignment deterministic inside each pair or cluster once the unit is randomized."
    )
    notes = [
        "Pre-register the estimand, alpha, minimum detectable effect, and stopping rule.",
        "Monitor sample ratio mismatch and attrition before locking the primary analysis.",
    ]
    if clustering_present or design_type == "clustered":
        notes.append("Report cluster counts, average cluster size, ICC estimate, and cluster-robust standard errors.")
    return AnalysisPlan(
        design_type=design_type,
        outcome_type=outcome_type,
        estimand=estimand,
        statistical_test=test,
        adjustment_recommendation=adjustment,
        randomization_recommendation=randomization,
        notes=notes,
    )
