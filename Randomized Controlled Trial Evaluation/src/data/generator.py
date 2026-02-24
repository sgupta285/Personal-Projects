"""
Synthetic RCT Data Generator.

Generates a clinical / policy trial dataset with:
- Random assignment to treatment/control
- Four compliance types: always-takers, never-takers, compliers, defiers
- Baseline covariates (age, gender, severity, pre-treatment outcome, biomarkers)
- Heterogeneous treatment effects (CATE) by age, gender, severity
- Known true ATE, LATE (complier-specific), ITT for method validation
- Attrition (non-random dropout)
- Potential outcomes framework (Y(0), Y(1)) for oracle comparison
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict
import structlog

from src.config import config

logger = structlog.get_logger()


COMPLIANCE_TYPES = ["complier", "always_taker", "never_taker"]


def generate_rct_data(
    n_subjects: int = 5000,
    treatment_fraction: float = 0.50,
    seed: int = 42,
) -> Tuple[pd.DataFrame, Dict]:
    """
    Generate synthetic RCT data with known causal effects and compliance structure.

    Compliance framework (monotonicity assumed, no defiers):
    - Compliers: take treatment iff assigned (D(1)=1, D(0)=0)
    - Always-takers: always take treatment regardless (D(1)=1, D(0)=1)
    - Never-takers: never take treatment regardless (D(1)=0, D(0)=0)

    LATE = ATE among compliers = E[Y(1)-Y(0) | complier]

    Returns:
        df: Subject-level data
        true_params: Dictionary of true causal parameters
    """
    np.random.seed(seed)
    cfg = config.data
    n = n_subjects

    # --- Covariates ---
    age = np.random.normal(50, 15, n).clip(18, 85)
    age_group = np.where(age < 35, "young", np.where(age < 55, "middle", "old"))
    gender = np.random.choice(["male", "female"], n, p=[0.52, 0.48])
    severity = np.random.choice(["mild", "moderate", "severe"], n, p=[0.40, 0.40, 0.20])
    bmi = np.random.normal(27, 5, n).clip(15, 50)
    biomarker_a = np.random.normal(100, 20, n)   # Continuous biomarker
    biomarker_b = np.random.choice([0, 1], n, p=[0.6, 0.4])  # Binary biomarker
    pre_outcome = (50 + 0.3 * age
                   - 5 * (severity == "severe").astype(float)
                   - 2 * (severity == "moderate").astype(float)
                   + 0.1 * biomarker_a
                   + np.random.randn(n) * 6)

    # --- Compliance Type Assignment ---
    # Compliance is a latent characteristic (pre-randomization)
    compliance_probs = np.zeros((n, 3))  # [complier, always_taker, never_taker]
    for i in range(n):
        # Compliance propensity varies by severity and age
        if severity[i] == "severe":
            compliance_probs[i] = [0.80, 0.12, 0.08]
        elif severity[i] == "moderate":
            compliance_probs[i] = [0.85, 0.06, 0.09]
        else:
            compliance_probs[i] = [0.88, cfg.noncompliance_always_taker, cfg.noncompliance_never_taker]

        # Older patients slightly less compliant
        if age[i] > 65:
            compliance_probs[i, 2] += 0.03
            compliance_probs[i, 0] -= 0.03

        compliance_probs[i] = compliance_probs[i] / compliance_probs[i].sum()

    compliance_type = np.array([
        np.random.choice(COMPLIANCE_TYPES, p=compliance_probs[i])
        for i in range(n)
    ])

    # --- Random Assignment (Z) ---
    n_treat = int(n * treatment_fraction)
    assignment = np.zeros(n, dtype=int)
    treat_idx = np.random.choice(n, n_treat, replace=False)
    assignment[treat_idx] = 1

    # --- Actual Treatment Received (D) ---
    actual_treatment = np.zeros(n, dtype=int)
    for i in range(n):
        if compliance_type[i] == "complier":
            actual_treatment[i] = assignment[i]  # Complies with assignment
        elif compliance_type[i] == "always_taker":
            actual_treatment[i] = 1               # Always takes treatment
        elif compliance_type[i] == "never_taker":
            actual_treatment[i] = 0               # Never takes treatment

    # --- Heterogeneous Treatment Effects ---
    individual_te = np.zeros(n)
    for i in range(n):
        # Age-based CATE
        te_age = cfg.cate_by_age.get(age_group[i], cfg.ate)
        # Severity-based CATE
        te_sev = cfg.cate_by_severity.get(severity[i], cfg.ate)
        # Gender-based CATE
        te_gen = cfg.cate_by_gender.get(gender[i], cfg.ate)

        # Combine: weighted average + biomarker interaction
        individual_te[i] = (0.35 * te_age + 0.35 * te_sev + 0.20 * te_gen
                            + 0.10 * (biomarker_b[i] * 1.5)
                            + np.random.randn() * 0.4)

    # --- Potential Outcomes ---
    y0 = (30
          + 0.2 * age
          - 3.0 * (gender == "female").astype(float)
          + 5.0 * (severity == "severe").astype(float)
          + 2.0 * (severity == "moderate").astype(float)
          + 0.3 * bmi
          + 0.15 * biomarker_a
          + 0.4 * pre_outcome
          + np.random.randn(n) * cfg.outcome_noise_std)

    y1 = y0 + individual_te

    # Observed outcome (depends on ACTUAL treatment)
    observed_outcome = np.where(actual_treatment == 1, y1, y0)

    # --- Attrition ---
    # Non-random: sicker patients and control group more likely to drop out
    attrition_prob = np.full(n, cfg.attrition_rate)
    attrition_prob += 0.02 * (severity == "severe").astype(float)
    attrition_prob += 0.01 * (1 - assignment)  # Control slightly more attrition
    attrition_prob = np.clip(attrition_prob, 0, 0.25)
    attrited = np.random.binomial(1, attrition_prob).astype(bool)

    # --- Build DataFrame ---
    df = pd.DataFrame({
        "subject_id": [f"S{i:05d}" for i in range(n)],
        "age": np.round(age, 1),
        "age_group": age_group,
        "gender": gender,
        "severity": severity,
        "bmi": np.round(bmi, 1),
        "biomarker_a": np.round(biomarker_a, 1),
        "biomarker_b": biomarker_b,
        "pre_outcome": np.round(pre_outcome, 2),
        "assigned_treatment": assignment,        # Z (instrument)
        "actual_treatment": actual_treatment,    # D (endogenous)
        "compliance_type": compliance_type,
        "compliant": (assignment == actual_treatment).astype(int),
        "outcome": np.round(observed_outcome, 2),
        "y0": np.round(y0, 2),                  # Oracle: Y(0)
        "y1": np.round(y1, 2),                  # Oracle: Y(1)
        "individual_te": np.round(individual_te, 2),
        "attrited": attrited,
    })

    # --- True Parameters ---
    complier_mask = compliance_type == "complier"
    true_params = {
        "ate": round(individual_te.mean(), 4),
        "att": round(individual_te[actual_treatment == 1].mean(), 4),
        "late": round(individual_te[complier_mask].mean(), 4),
        "itt": round(np.mean(y1[assignment == 1]) - np.mean(y0[assignment == 0]), 4),
        "cate_by_age": {k: round(individual_te[age_group == k].mean(), 4)
                        for k in ["young", "middle", "old"]},
        "cate_by_severity": {k: round(individual_te[severity == k].mean(), 4)
                             for k in ["mild", "moderate", "severe"]},
        "cate_by_gender": {k: round(individual_te[gender == k].mean(), 4)
                           for k in ["male", "female"]},
        "compliance_rates": {
            "complier": round(complier_mask.mean(), 4),
            "always_taker": round((compliance_type == "always_taker").mean(), 4),
            "never_taker": round((compliance_type == "never_taker").mean(), 4),
        },
        "first_stage": round(actual_treatment[assignment == 1].mean()
                             - actual_treatment[assignment == 0].mean(), 4),
        "attrition_rate": round(attrited.mean(), 4),
        "n_treatment": int(assignment.sum()),
        "n_control": int(n - assignment.sum()),
    }

    logger.info("rct_data_generated", n=n, true_ate=true_params["ate"],
                true_late=true_params["late"],
                compliance=true_params["compliance_rates"],
                first_stage=true_params["first_stage"])

    return df, true_params
