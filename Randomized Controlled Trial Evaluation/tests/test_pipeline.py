"""Test suite for RCT Evaluation Framework."""

import numpy as np
import pandas as pd
import pytest

from src.data.generator import generate_rct_data
from src.estimation.ate_estimators import (
    difference_in_means, lin_estimator, cuped_estimator,
    bootstrap_ate, permutation_test,
)
from src.estimation.iv_late import (
    wald_estimator, tsls_estimator, hausman_test, analyze_compliance,
)
from src.estimation.heterogeneity import (
    estimate_cate_subgroup, interaction_regression,
    CausalForestEstimator, estimate_gates, blp_test,
)
from src.diagnostics.checks import (
    covariate_balance, attrition_analysis, holm_correction,
    benjamini_hochberg, power_analysis,
)


# ============================================================
# DATA GENERATION
# ============================================================

class TestDataGenerator:
    def setup_method(self):
        self.df, self.params = generate_rct_data(n_subjects=2000, seed=42)

    def test_correct_size(self):
        assert len(self.df) == 2000

    def test_treatment_balanced(self):
        vc = self.df["assigned_treatment"].value_counts()
        assert abs(vc[0] - vc[1]) < 200

    def test_no_missing_outcomes(self):
        assert not self.df["outcome"].isna().any()

    def test_positive_ages(self):
        assert (self.df["age"] >= 18).all()

    def test_compliance_types_present(self):
        types = self.df["compliance_type"].unique()
        assert "complier" in types
        assert "always_taker" in types
        assert "never_taker" in types

    def test_actual_treatment_differs_from_assignment(self):
        # Some subjects should differ (non-compliance)
        n_differ = (self.df["assigned_treatment"] != self.df["actual_treatment"]).sum()
        assert n_differ > 0

    def test_true_params_populated(self):
        assert "ate" in self.params
        assert "late" in self.params
        assert "first_stage" in self.params
        assert "cate_by_age" in self.params

    def test_potential_outcomes_exist(self):
        assert "y0" in self.df.columns
        assert "y1" in self.df.columns

    def test_attrition_exists(self):
        assert self.df["attrited"].sum() > 0


# ============================================================
# ATE / ITT ESTIMATION
# ============================================================

class TestATEEstimation:
    def setup_method(self):
        self.df, self.params = generate_rct_data(n_subjects=3000, seed=42)
        self.df = self.df[~self.df["attrited"]].copy()

    def test_dim_positive_effect(self):
        r = difference_in_means(self.df)
        assert r.estimate > 0  # Treatment should help (known DGP)

    def test_dim_significant(self):
        r = difference_in_means(self.df)
        assert r.p_value < 0.10

    def test_lin_reduces_variance(self):
        dim = difference_in_means(self.df)
        lin = lin_estimator(self.df)
        assert lin.variance_reduction_pct > 0
        assert lin.std_error <= dim.std_error * 1.05  # Lin should be at least as precise

    def test_cuped_reduces_variance(self):
        dim = difference_in_means(self.df)
        cuped = cuped_estimator(self.df)
        assert cuped.variance_reduction_pct > 0

    def test_bootstrap_ci_covers_estimate(self):
        ate, lo, hi, _ = bootstrap_ate(self.df, n_bootstrap=500)
        assert lo <= ate <= hi

    def test_permutation_significant(self):
        stat, p, _ = permutation_test(self.df, n_permutations=1000)
        assert stat > 0  # Positive treatment effect
        assert p < 0.10


# ============================================================
# LATE / 2SLS
# ============================================================

class TestIVLATE:
    def setup_method(self):
        self.df, self.params = generate_rct_data(n_subjects=3000, seed=42)
        self.df = self.df[~self.df["attrited"]].copy()

    def test_wald_positive(self):
        r = wald_estimator(self.df, true_late=self.params["late"])
        assert r.estimate > 0

    def test_wald_larger_than_itt(self):
        """LATE should be larger than ITT when there's non-compliance."""
        itt = difference_in_means(self.df)
        late = wald_estimator(self.df)
        # LATE = ITT / compliance_rate, so LATE > ITT when compliance < 1
        assert abs(late.estimate) >= abs(itt.estimate) * 0.9  # Allow small noise

    def test_first_stage_strong(self):
        r = wald_estimator(self.df)
        assert r.first_stage.f_statistic > 10
        assert r.first_stage.is_strong

    def test_tsls_with_covariates(self):
        r = tsls_estimator(self.df, true_late=self.params["late"])
        assert r.estimate > 0
        assert r.std_error > 0

    def test_tsls_near_true_late(self):
        r = tsls_estimator(self.df, true_late=self.params["late"])
        assert abs(r.estimate - self.params["late"]) < 2.0  # Within 2 units

    def test_hausman_produces_result(self):
        h = hausman_test(self.df)
        assert h.ols_estimate != 0
        assert h.iv_estimate != 0

    def test_compliance_analysis(self):
        c = analyze_compliance(self.df)
        assert c.complier_share > 0.5  # Most are compliers
        assert abs(c.complier_share + c.always_taker_share + c.never_taker_share - 1.0) < 0.01


# ============================================================
# HETEROGENEITY
# ============================================================

class TestHeterogeneity:
    def setup_method(self):
        self.df, self.params = generate_rct_data(n_subjects=3000, seed=42)
        self.df = self.df[~self.df["attrited"]].copy()

    def test_cate_by_age(self):
        cate = estimate_cate_subgroup(self.df, subgroup_col="age_group",
                                       true_cate=self.params["cate_by_age"])
        assert len(cate) == 3  # young, middle, old
        # Young should have higher effect than old (by DGP)
        young = next(c for c in cate if c.subgroup_value == "young")
        old = next(c for c in cate if c.subgroup_value == "old")
        assert young.estimate > old.estimate

    def test_cate_by_severity(self):
        cate = estimate_cate_subgroup(self.df, subgroup_col="severity",
                                       true_cate=self.params["cate_by_severity"])
        # Severe should have highest CATE (by DGP)
        severe = next(c for c in cate if c.subgroup_value == "severe")
        mild = next(c for c in cate if c.subgroup_value == "mild")
        assert severe.estimate > mild.estimate

    def test_interaction_regression(self):
        r = interaction_regression(self.df)
        assert r.base_ate > 0
        assert r.n_obs > 0
        assert len(r.interactions) > 0

    def test_causal_forest_predictions(self):
        cf = CausalForestEstimator(n_trees=100, min_samples_leaf=50)
        r = cf.estimate(self.df)
        assert len(r.cate_predictions) == len(self.df)
        assert r.cate_std > 0  # Some heterogeneity
        assert r.ate_estimate > 0

    def test_causal_forest_feature_importance(self):
        cf = CausalForestEstimator(n_trees=100, min_samples_leaf=50)
        r = cf.estimate(self.df)
        assert len(r.feature_importances) > 0
        assert sum(r.feature_importances.values()) > 0

    def test_gates(self):
        cf = CausalForestEstimator(n_trees=100, min_samples_leaf=50)
        cf_r = cf.estimate(self.df)
        gates = estimate_gates(self.df, cf_r.cate_predictions, n_groups=5)
        assert len(gates.group_estimates) == 5
        assert len(gates.group_sizes) == 5
        # Highest quintile should have higher GATE than lowest
        assert gates.group_estimates[-1] > gates.group_estimates[0]

    def test_blp(self):
        cf = CausalForestEstimator(n_trees=100, min_samples_leaf=50)
        cf_r = cf.estimate(self.df)
        blp = blp_test(self.df, cf_r.cate_predictions)
        assert blp.beta_1 > 0  # Should detect heterogeneity


# ============================================================
# DIAGNOSTICS
# ============================================================

class TestDiagnostics:
    def setup_method(self):
        self.df, self.params = generate_rct_data(n_subjects=2000, seed=42)

    def test_balance_table(self):
        bal = covariate_balance(self.df)
        assert len(bal.rows) >= 3
        assert bal.n_treatment > 0
        assert bal.n_control > 0
        # In an RCT, balance should hold
        assert bal.max_smd < 0.20

    def test_balance_joint_test(self):
        bal = covariate_balance(self.df)
        # Joint F-test should not reject (RCT → covariates don't predict treatment)
        assert bal.joint_f_p > 0.01

    def test_attrition(self):
        att = attrition_analysis(self.df)
        assert 0 < att.overall_rate < 0.20
        assert att.treatment_rate >= 0
        assert att.control_rate >= 0

    def test_lee_bounds(self):
        att = attrition_analysis(self.df)
        if att.lee_bounds:
            lo, hi = att.lee_bounds
            assert lo <= hi

    def test_holm_correction(self):
        p_vals = [0.01, 0.03, 0.08]
        corrected = holm_correction(p_vals, 0.05)
        assert len(corrected) == 3
        # First should still be significant after correction
        assert corrected[0][1] is True

    def test_bh_correction(self):
        p_vals = [0.01, 0.03, 0.08]
        corrected = benjamini_hochberg(p_vals, 0.05)
        assert len(corrected) == 3

    def test_power_analysis(self):
        pwr = power_analysis(baseline_std=10, mde=2.0)
        assert pwr.sample_size_per_arm > 100
        assert pwr.total_sample_size == 2 * pwr.sample_size_per_arm


# ============================================================
# INTEGRATION
# ============================================================

class TestIntegration:
    def test_full_pipeline(self):
        """End-to-end: data → ITT → LATE → heterogeneity."""
        df, params = generate_rct_data(n_subjects=1500, seed=42)
        analysis = df[~df["attrited"]].copy()

        # ITT
        dim = difference_in_means(analysis)
        assert dim.estimate > 0

        # LATE
        late = wald_estimator(analysis, true_late=params["late"])
        assert late.first_stage.is_strong

        # 2SLS
        tsls = tsls_estimator(analysis, true_late=params["late"])
        assert tsls.estimate > 0

        # Heterogeneity
        cate = estimate_cate_subgroup(analysis, subgroup_col="severity")
        assert len(cate) >= 2

        # Causal forest + GATES
        cf = CausalForestEstimator(n_trees=50, min_samples_leaf=50)
        cf_r = cf.estimate(analysis)
        gates = estimate_gates(analysis, cf_r.cate_predictions, n_groups=4)
        assert len(gates.group_estimates) == 4

        # Diagnostics
        bal = covariate_balance(analysis)
        assert bal.n_treatment > 0

    def test_late_vs_itt_relationship(self):
        """LATE should be ITT / compliance_rate for simple Wald."""
        df, params = generate_rct_data(n_subjects=5000, seed=42)
        analysis = df[~df["attrited"]].copy()

        itt = difference_in_means(analysis)
        late = wald_estimator(analysis)
        compliance = analyze_compliance(analysis)

        # LATE ≈ ITT / compliance_rate
        expected_late = itt.estimate / compliance.complier_share if compliance.complier_share > 0 else 0
        assert abs(late.estimate - expected_late) < 1.0  # Should be close
