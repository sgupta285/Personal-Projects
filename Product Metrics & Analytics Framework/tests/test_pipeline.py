"""Test suite for Product Metrics & Analytics Framework."""

import numpy as np
import pandas as pd
import pytest

from src.data.generator import generate_product_data, ONBOARDING_FUNNEL
from src.metrics.engagement import EngagementAnalyzer
from src.metrics.retention import RetentionAnalyzer
from src.metrics.funnel_revenue import FunnelAnalyzer, RevenueAnalyzer
from src.experimentation.ab_testing import (
    FrequentistTester, BayesianTester, SequentialTester, PowerCalculator,
)
from src.segmentation.segments import RFMSegmenter, BehavioralClusterer


# ── Data Generation ──

class TestDataGenerator:
    def setup_method(self):
        self.users, self.sessions, self.events = generate_product_data(
            n_users=1000, n_days=60, seed=42
        )

    def test_user_count(self):
        assert len(self.users) == 1000

    def test_no_missing_ids(self):
        assert not self.users["user_id"].isna().any()
        assert not self.sessions["user_id"].isna().any()

    def test_variants_balanced(self):
        vc = self.users["variant"].value_counts()
        assert abs(vc["control"] - vc["treatment"]) < 100

    def test_sessions_have_positive_duration(self):
        assert (self.sessions["duration_sec"] > 0).all()

    def test_events_linked_to_sessions(self):
        assert self.events["user_id"].isin(self.users["user_id"]).all()


# ── Engagement ──

class TestEngagement:
    def setup_method(self):
        self.users, self.sessions, self.events = generate_product_data(
            n_users=500, n_days=30, seed=42
        )
        self.analyzer = EngagementAnalyzer()

    def test_dau_wau_mau_computed(self):
        metrics = self.analyzer.compute_dau_wau_mau(self.sessions)
        assert "dau" in metrics.columns
        assert "wau" in metrics.columns
        assert "mau" in metrics.columns
        assert (metrics["dau"] <= metrics["wau"]).all()
        assert (metrics["wau"] <= metrics["mau"]).all()

    def test_stickiness_bounded(self):
        metrics = self.analyzer.compute_dau_wau_mau(self.sessions)
        assert (metrics["stickiness"] >= 0).all()
        assert (metrics["stickiness"] <= 1).all()

    def test_feature_adoption(self):
        adoption = self.analyzer.compute_feature_adoption(
            self.sessions, self.events, ["feed", "search"], 200
        )
        assert len(adoption) == 2
        assert all(0 <= a.adoption_rate <= 1 for a in adoption)


# ── Retention ──

class TestRetention:
    def setup_method(self):
        self.users, self.sessions, _ = generate_product_data(
            n_users=500, n_days=60, seed=42
        )
        self.analyzer = RetentionAnalyzer()

    def test_cohort_table_shape(self):
        table = self.analyzer.build_cohort_table(self.users, self.sessions, "W", 8)
        assert table.shape[1] >= 1

    def test_retention_curve_decreasing(self):
        curve = self.analyzer.compute_retention_curve(
            self.users, self.sessions, [1, 7, 14, 30]
        )
        if len(curve) >= 2:
            # Retention should generally decrease over time
            assert curve.iloc[0]["retention_rate"] >= curve.iloc[-1]["retention_rate"]

    def test_churn_estimation(self):
        curve = self.analyzer.compute_retention_curve(
            self.users, self.sessions, [1, 7, 14, 30]
        )
        churn = self.analyzer.estimate_churn_rate(curve)
        assert "daily_churn" in churn
        assert 0 <= churn["daily_churn"] <= 1


# ── Funnel ──

class TestFunnel:
    def setup_method(self):
        self.users, _, _ = generate_product_data(n_users=500, n_days=30, seed=42)
        self.analyzer = FunnelAnalyzer()

    def test_funnel_stages(self):
        result = self.analyzer.analyze_funnel(self.users, ONBOARDING_FUNNEL)
        assert len(result.stages) == len(ONBOARDING_FUNNEL)
        # Each stage <= previous
        for i in range(1, len(result.stages)):
            assert result.stages[i].users <= result.stages[i - 1].users

    def test_overall_conversion(self):
        result = self.analyzer.analyze_funnel(self.users, ONBOARDING_FUNNEL)
        assert 0 <= result.overall_conversion <= 1


# ── A/B Testing ──

class TestABTesting:
    def test_proportion_test_detects_difference(self):
        np.random.seed(42)
        control = np.random.binomial(1, 0.10, 5000).astype(float)
        treatment = np.random.binomial(1, 0.13, 5000).astype(float)
        tester = FrequentistTester()
        r = tester.test_proportion(control, treatment, "conversion")
        assert r.treatment_mean > r.control_mean
        assert r.p_value < 0.10  # Should detect with 5K per group

    def test_no_difference_detected(self):
        np.random.seed(42)
        a = np.random.binomial(1, 0.10, 1000).astype(float)
        b = np.random.binomial(1, 0.10, 1000).astype(float)
        tester = FrequentistTester()
        r = tester.test_proportion(a, b, "conversion")
        # Should not be significant (same rate)
        assert r.p_value > 0.01  # Very unlikely to be significant

    def test_continuous_test(self):
        np.random.seed(42)
        control = np.random.normal(50, 10, 1000)
        treatment = np.random.normal(53, 10, 1000)
        tester = FrequentistTester()
        r = tester.test_continuous(control, treatment, "revenue")
        assert r.absolute_lift > 0

    def test_bayesian(self):
        np.random.seed(42)
        control = np.random.binomial(1, 0.10, 5000).astype(float)
        treatment = np.random.binomial(1, 0.13, 5000).astype(float)
        tester = BayesianTester()
        r = tester.test_proportion(control, treatment, "conv")
        assert 0 <= r.prob_treatment_better <= 1

    def test_sequential(self):
        np.random.seed(42)
        control = np.random.binomial(1, 0.10, 5000).astype(float)
        treatment = np.random.binomial(1, 0.14, 5000).astype(float)
        tester = SequentialTester()
        results = tester.sequential_test(control, treatment, n_looks=5)
        assert len(results) == 5

    def test_bonferroni(self):
        p_vals = [0.01, 0.04, 0.06]
        corrected = FrequentistTester.bonferroni_correction(p_vals, 0.05)
        # 0.05/3 = 0.0167 → only first should pass
        assert corrected[0][1] is True
        assert corrected[1][1] is False

    def test_power_calculation(self):
        n = PowerCalculator.sample_size_proportion(0.10, 0.02)
        assert n > 1000  # Should need substantial sample
        assert n < 100000


# ── Segmentation ──

class TestSegmentation:
    def setup_method(self):
        self.users, self.sessions, _ = generate_product_data(
            n_users=500, n_days=60, seed=42
        )

    def test_rfm_scoring(self):
        rfm = RFMSegmenter()
        result = rfm.compute_rfm(self.users, self.sessions)
        assert "R_score" in result.columns
        assert "segment" in result.columns
        assert result["R_score"].between(1, 5).all()

    def test_rfm_segments(self):
        rfm = RFMSegmenter()
        rfm_df = rfm.compute_rfm(self.users, self.sessions)
        segments = rfm.segment_summary(rfm_df)
        total = sum(s.n_users for s in segments)
        assert total == len(rfm_df)

    def test_behavioral_clustering(self):
        clusterer = BehavioralClusterer()
        result = clusterer.cluster_users(self.users, self.sessions, n_clusters=4)
        assert "cluster" in result.columns
        assert result["cluster"].nunique() == 4


# ── Revenue ──

class TestRevenue:
    def setup_method(self):
        self.users, _, self.events = generate_product_data(
            n_users=500, n_days=60, seed=42
        )

    def test_revenue_metrics(self):
        analyzer = RevenueAnalyzer()
        rev = analyzer.compute_revenue_metrics(self.users, self.events)
        assert rev.arpu >= 0
        assert rev.arppu >= rev.arpu
        assert 0 <= rev.paying_user_pct <= 1


# ── Integration ──

class TestIntegration:
    def test_full_pipeline(self):
        users, sessions, events = generate_product_data(
            n_users=300, n_days=30, seed=42
        )
        # Engagement
        ea = EngagementAnalyzer()
        metrics = ea.compute_dau_wau_mau(sessions)
        assert len(metrics) > 0

        # Retention
        ra = RetentionAnalyzer()
        curve = ra.compute_retention_curve(users, sessions, [1, 7])
        assert len(curve) >= 1

        # Funnel
        fa = FunnelAnalyzer()
        funnel = fa.analyze_funnel(users, ONBOARDING_FUNNEL)
        assert funnel.overall_conversion > 0

        # A/B test
        ctrl = users[users["variant"] == "control"]["completed_onboarding"].values.astype(float)
        treat = users[users["variant"] == "treatment"]["completed_onboarding"].values.astype(float)
        if len(ctrl) > 10 and len(treat) > 10:
            ft = FrequentistTester()
            r = ft.test_proportion(ctrl, treat, "onboarding")
            assert r.n_control > 0
