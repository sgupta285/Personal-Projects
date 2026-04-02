from __future__ import annotations

from dataclasses import asdict, dataclass
from math import ceil, sqrt
from typing import Literal

import numpy as np
from scipy.optimize import brentq
from statsmodels.stats.power import TTestIndPower, TTestPower, zt_ind_solve_power
from statsmodels.stats.proportion import proportion_effectsize


OutcomeType = Literal["continuous", "binary"]


@dataclass(slots=True)
class SampleSizeRecommendation:
    design_type: str
    outcome_type: OutcomeType
    alpha: float
    target_power: float
    effect_size: float
    treatment_ratio: float
    total_required_n: int
    treatment_n: int
    control_n: int
    estimated_cost: float
    minimum_detectable_effect: float
    notes: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class TwoSampleDesignInputs:
    outcome_type: OutcomeType = "continuous"
    alpha: float = 0.05
    power: float = 0.8
    effect_size: float = 0.3
    baseline_rate: float = 0.2
    alternative_rate: float = 0.24
    treatment_cost: float = 1.0
    control_cost: float = 1.0
    variance_ratio: float = 1.0
    budget: float | None = None


@dataclass(slots=True)
class PairedDesignInputs:
    alpha: float = 0.05
    power: float = 0.8
    effect_size: float = 0.25
    cost_per_subject: float = 1.0
    budget: float | None = None


@dataclass(slots=True)
class ClusteredDesignInputs:
    alpha: float = 0.05
    power: float = 0.8
    effect_size: float = 0.3
    icc: float = 0.05
    avg_cluster_size: int = 20
    treatment_cost: float = 1.0
    control_cost: float = 1.0
    variance_ratio: float = 1.0
    budget: float | None = None


def optimal_allocation_ratio(
    cost_treatment: float,
    cost_control: float,
    variance_ratio: float = 1.0,
) -> float:
    if cost_treatment <= 0 or cost_control <= 0:
        raise ValueError("Costs must be positive.")
    if variance_ratio <= 0:
        raise ValueError("Variance ratio must be positive.")
    return sqrt(variance_ratio * cost_control / cost_treatment)


def _split_total_n(total_n: int, ratio: float) -> tuple[int, int]:
    control_n = max(2, round(total_n / (1 + ratio)))
    treatment_n = max(2, total_n - control_n)
    return treatment_n, control_n


def _total_cost(treatment_n: int, control_n: int, treatment_cost: float, control_cost: float) -> float:
    return treatment_n * treatment_cost + control_n * control_cost


def _binary_effect_size(baseline_rate: float, alternative_rate: float) -> float:
    if not 0 < baseline_rate < 1 or not 0 < alternative_rate < 1:
        raise ValueError("Rates must be between 0 and 1.")
    return float(abs(proportion_effectsize(alternative_rate, baseline_rate)))


def _mde_under_budget_continuous(
    alpha: float,
    power: float,
    ratio: float,
    max_total_n: int,
) -> float:
    def root_fn(effect_size: float) -> float:
        return zt_ind_solve_power(
            effect_size=effect_size,
            nobs1=max_total_n / (1 + ratio),
            alpha=alpha,
            power=None,
            ratio=ratio,
            alternative="two-sided",
        ) - power

    return float(brentq(root_fn, 1e-4, 3.0))


def recommend_two_sample_design(inputs: TwoSampleDesignInputs) -> SampleSizeRecommendation:
    ratio = optimal_allocation_ratio(
        cost_treatment=inputs.treatment_cost,
        cost_control=inputs.control_cost,
        variance_ratio=inputs.variance_ratio,
    )
    notes: list[str] = [
        "Uses cost-aware Neyman-style allocation when treatment and control costs differ.",
        "Reported MDE reflects the current budget when budget is supplied, otherwise it matches the requested effect size.",
    ]

    if inputs.outcome_type == "continuous":
        effect_size = inputs.effect_size
        n_control = zt_ind_solve_power(
            effect_size=effect_size,
            nobs1=None,
            alpha=inputs.alpha,
            power=inputs.power,
            ratio=ratio,
            alternative="two-sided",
        )
        control_n = int(ceil(n_control))
        treatment_n = int(ceil(control_n * ratio))
    else:
        effect_size = _binary_effect_size(inputs.baseline_rate, inputs.alternative_rate)
        analysis = TTestIndPower()
        control_n = int(
            ceil(
                analysis.solve_power(
                    effect_size=effect_size,
                    alpha=inputs.alpha,
                    power=inputs.power,
                    ratio=ratio,
                    alternative="two-sided",
                )
            )
        )
        treatment_n = int(ceil(control_n * ratio))

    total_required_n = treatment_n + control_n
    estimated_cost = _total_cost(treatment_n, control_n, inputs.treatment_cost, inputs.control_cost)
    mde = inputs.effect_size

    if inputs.budget is not None:
        max_total_n = int(
            (inputs.budget * (1 + ratio)) / (inputs.treatment_cost * ratio + inputs.control_cost)
        )
        max_total_n = max(max_total_n, 8)
        budget_treatment_n, budget_control_n = _split_total_n(max_total_n, ratio)
        estimated_cost = _total_cost(
            budget_treatment_n, budget_control_n, inputs.treatment_cost, inputs.control_cost
        )
        if inputs.outcome_type == "continuous":
            mde = _mde_under_budget_continuous(inputs.alpha, inputs.power, ratio, max_total_n)
        else:
            power_model = TTestIndPower()

            def root_fn(effect: float) -> float:
                return power_model.power(
                    effect_size=effect,
                    nobs1=budget_control_n,
                    alpha=inputs.alpha,
                    ratio=ratio,
                    alternative="two-sided",
                ) - inputs.power

            mde = float(brentq(root_fn, 1e-4, 2.0))
        notes.append("Budget was used to back out the smallest detectable standardized effect.")

    return SampleSizeRecommendation(
        design_type="between_subjects",
        outcome_type=inputs.outcome_type,
        alpha=inputs.alpha,
        target_power=inputs.power,
        effect_size=float(effect_size),
        treatment_ratio=float(ratio),
        total_required_n=int(total_required_n),
        treatment_n=int(treatment_n),
        control_n=int(control_n),
        estimated_cost=float(round(estimated_cost, 2)),
        minimum_detectable_effect=float(round(mde, 4)),
        notes=notes,
    )


def recommend_paired_design(inputs: PairedDesignInputs) -> SampleSizeRecommendation:
    analysis = TTestPower()
    pairs_required = int(
        ceil(
            analysis.solve_power(
                effect_size=inputs.effect_size,
                alpha=inputs.alpha,
                power=inputs.power,
                alternative="two-sided",
            )
        )
    )
    estimated_cost = pairs_required * inputs.cost_per_subject
    mde = inputs.effect_size
    if inputs.budget is not None:
        pairs_affordable = max(4, int(inputs.budget // inputs.cost_per_subject))

        def root_fn(effect: float) -> float:
            return analysis.power(
                effect_size=effect,
                nobs=pairs_affordable,
                alpha=inputs.alpha,
                alternative="two-sided",
            ) - inputs.power

        mde = float(brentq(root_fn, 1e-4, 2.0))
        estimated_cost = pairs_affordable * inputs.cost_per_subject

    return SampleSizeRecommendation(
        design_type="within_subjects",
        outcome_type="continuous",
        alpha=inputs.alpha,
        target_power=inputs.power,
        effect_size=float(inputs.effect_size),
        treatment_ratio=1.0,
        total_required_n=int(pairs_required),
        treatment_n=int(pairs_required),
        control_n=int(pairs_required),
        estimated_cost=float(round(estimated_cost, 2)),
        minimum_detectable_effect=float(round(mde, 4)),
        notes=[
            "Assumes a paired design where each subject is observed before and after treatment.",
            "Effect size is interpreted as the standardized mean difference in paired outcomes.",
        ],
    )


def recommend_clustered_design(inputs: ClusteredDesignInputs) -> SampleSizeRecommendation:
    base = recommend_two_sample_design(
        TwoSampleDesignInputs(
            outcome_type="continuous",
            alpha=inputs.alpha,
            power=inputs.power,
            effect_size=inputs.effect_size,
            treatment_cost=inputs.treatment_cost,
            control_cost=inputs.control_cost,
            variance_ratio=inputs.variance_ratio,
            budget=inputs.budget,
        )
    )
    design_effect = 1 + (inputs.avg_cluster_size - 1) * inputs.icc
    inflated_total_n = int(ceil(base.total_required_n * design_effect))
    treatment_n, control_n = _split_total_n(inflated_total_n, base.treatment_ratio)
    treatment_clusters = int(ceil(treatment_n / inputs.avg_cluster_size))
    control_clusters = int(ceil(control_n / inputs.avg_cluster_size))
    cost = _total_cost(treatment_n, control_n, inputs.treatment_cost, inputs.control_cost)

    notes = list(base.notes)
    notes.extend(
        [
            f"Clustered design inflates the individual-level sample size by a design effect of {design_effect:.3f}.",
            f"Requires about {treatment_clusters} treatment clusters and {control_clusters} control clusters.",
        ]
    )

    return SampleSizeRecommendation(
        design_type="clustered",
        outcome_type="continuous",
        alpha=inputs.alpha,
        target_power=inputs.power,
        effect_size=float(inputs.effect_size),
        treatment_ratio=base.treatment_ratio,
        total_required_n=int(inflated_total_n),
        treatment_n=int(treatment_n),
        control_n=int(control_n),
        estimated_cost=float(round(cost, 2)),
        minimum_detectable_effect=base.minimum_detectable_effect,
        notes=notes,
    )


def cost_curve(
    max_budget: int,
    design: Literal["between", "paired", "clustered"],
    effect_size: float,
    alpha: float = 0.05,
    power: float = 0.8,
) -> list[dict]:
    results: list[dict] = []
    for budget in np.linspace(max(50, max_budget * 0.1), max_budget, num=12):
        if design == "between":
            rec = recommend_two_sample_design(
                TwoSampleDesignInputs(effect_size=effect_size, alpha=alpha, power=power, budget=float(budget))
            )
        elif design == "paired":
            rec = recommend_paired_design(
                PairedDesignInputs(effect_size=effect_size, alpha=alpha, power=power, budget=float(budget))
            )
        else:
            rec = recommend_clustered_design(
                ClusteredDesignInputs(effect_size=effect_size, alpha=alpha, power=power, budget=float(budget))
            )
        results.append(
            {
                "budget": round(float(budget), 2),
                "mde": rec.minimum_detectable_effect,
                "estimated_cost": rec.estimated_cost,
                "required_n": rec.total_required_n,
            }
        )
    return results
