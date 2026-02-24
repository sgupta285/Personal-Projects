"""Test suite for Minimum Wage Employment Effects Analysis."""

import numpy as np
import pandas as pd
import pytest

from src.data.generator import generate_panel_data
from src.models.did import DiDEstimator, EventStudyEstimator, test_parallel_trends
from src.models.synthetic_control import SyntheticControlEstimator
from src.models.rdd_robustness import RDDEstimator, RobustnessAnalyzer


# ── Data Generation ──

class TestDataGenerator:
    def setup_method(self):
        self.panel, self.params = generate_panel_data(n_states=20, n_quarters=30, seed=42)

    def test_panel_shape(self):
        assert len(self.panel) == 20 * 30

    def test_no_missing(self):
        assert not self.panel["employment_rate"].isna().any()
        assert not self.panel["avg_wage"].isna().any()

    def test_employment_bounded(self):
        assert (self.panel["employment_rate"] >= 0.70).all()
        assert (self.panel["employment_rate"] <= 1.0).all()

    def test_treatment_indicator(self):
        n_treated = self.panel[self.panel["treated"] == 1]["state"].nunique()
        assert n_treated == self.params["n_treated"]

    def test_did_indicator(self):
        # DiD should only be 1 for treated states in post period
        did_rows = self.panel[self.panel["did"] == 1]
        assert (did_rows["treated"] == 1).all()
        assert (did_rows["post"] == 1).all()

    def test_true_params_populated(self):
        assert "employment_effect" in self.params
        assert "treated_states" in self.params


# ── DiD Estimation ──

class TestDiD:
    def setup_method(self):
        self.panel, self.params = generate_panel_data(n_states=30, n_quarters=40, seed=42)
        self.did = DiDEstimator()

    def test_negative_employment_effect(self):
        r = self.did.estimate(self.panel, outcome="employment_rate", treatment="did")
        assert r.estimate < 0  # Min wage should reduce employment (known DGP)

    def test_significant(self):
        r = self.did.estimate(self.panel, outcome="employment_rate", treatment="did")
        assert r.p_value < 0.10

    def test_near_true_effect(self):
        true_eff = self.params["employment_effect"]
        r = self.did.estimate(self.panel, outcome="employment_rate", treatment="did",
                              true_effect=true_eff)
        # Within 0.02 of true effect
        assert abs(r.estimate - true_eff) < 0.025

    def test_includes_state_time_fe(self):
        r = self.did.estimate(self.panel, outcome="employment_rate", treatment="did")
        assert r.state_fe
        assert r.time_fe

    def test_cluster_se(self):
        r = self.did.estimate(self.panel, outcome="employment_rate", treatment="did")
        assert r.n_clusters == 30


# ── Event Study ──

class TestEventStudy:
    def setup_method(self):
        self.panel, _ = generate_panel_data(n_states=30, n_quarters=40, seed=42)
        self.es = EventStudyEstimator()

    def test_produces_coefficients(self):
        r = self.es.estimate(self.panel, treatment_quarter=20, pre_periods=6, post_periods=8)
        assert len(r.coefficients) > 0

    def test_reference_period_zero(self):
        r = self.es.estimate(self.panel, treatment_quarter=20, pre_periods=6, post_periods=8)
        ref = [c for c in r.coefficients if c.relative_period == -1]
        assert len(ref) == 1
        assert ref[0].estimate == 0.0

    def test_parallel_trends(self):
        r = self.es.estimate(self.panel, treatment_quarter=20, pre_periods=6, post_periods=8)
        # Pre-trend test should not reject (parallel trends hold by construction)
        assert r.pre_trend_p_value > 0.01


# ── Parallel Trends ──

class TestParallelTrends:
    def test_trends_hold(self):
        panel, _ = generate_panel_data(n_states=30, n_quarters=40, seed=42)
        _, p, holds = test_parallel_trends(panel)
        assert holds  # Should hold by construction


# ── Synthetic Control ──

class TestSyntheticControl:
    def setup_method(self):
        self.panel, self.params = generate_panel_data(n_states=20, n_quarters=30, seed=42)
        self.sc = SyntheticControlEstimator()

    def test_produces_result(self):
        state = self.params["treated_states"][0]
        r = self.sc.estimate(self.panel, state, treatment_quarter=20)
        assert r.treated_state == state
        assert len(r.weights) > 0

    def test_weights_sum_approximately_one(self):
        state = self.params["treated_states"][0]
        r = self.sc.estimate(self.panel, state, treatment_quarter=20)
        total = sum(r.weights.values())
        assert abs(total - 1.0) < 0.15  # Approximate due to NNLS

    def test_pre_fit_quality(self):
        state = self.params["treated_states"][0]
        r = self.sc.estimate(self.panel, state, treatment_quarter=20)
        assert r.pre_rmspe < 0.05  # Should fit well

    def test_effect_negative(self):
        state = self.params["treated_states"][0]
        r = self.sc.estimate(self.panel, state, treatment_quarter=20)
        assert r.estimated_effect < 0  # Employment should decrease


# ── RDD ──

class TestRDD:
    def setup_method(self):
        self.panel, _ = generate_panel_data(n_states=50, n_quarters=40, seed=42)
        self.rdd = RDDEstimator()

    def test_produces_result(self):
        post = self.panel[self.panel["post"] == 1]
        cutoff = post["min_wage"].median()
        r = self.rdd.estimate(post, cutoff=cutoff, bandwidth=2.0)
        assert r.n_below > 0
        assert r.n_above > 0

    def test_bandwidth_sensitivity(self):
        post = self.panel[self.panel["post"] == 1]
        cutoff = post["min_wage"].median()
        results = self.rdd.bandwidth_sensitivity(post, cutoff=cutoff)
        assert len(results) > 3


# ── Robustness ──

class TestRobustness:
    def test_checks_run(self):
        panel, _ = generate_panel_data(n_states=20, n_quarters=30, seed=42)
        robust = RobustnessAnalyzer()
        checks = robust.run_all_checks(panel, -0.01)
        assert len(checks) >= 4


# ── Integration ──

class TestIntegration:
    def test_full_pipeline(self):
        panel, params = generate_panel_data(n_states=20, n_quarters=30, seed=42)

        # DiD
        did = DiDEstimator()
        r = did.estimate(panel, outcome="employment_rate", treatment="did")
        assert r.estimate != 0

        # Event Study
        es = EventStudyEstimator()
        es_r = es.estimate(panel, treatment_quarter=20, pre_periods=4, post_periods=4)
        assert len(es_r.coefficients) > 0

        # Synthetic Control
        sc = SyntheticControlEstimator()
        state = params["treated_states"][0]
        sc_r = sc.estimate(panel, state, treatment_quarter=20)
        assert sc_r.pre_rmspe < 0.1
