"""
Test suite for Demand Elasticity Analysis.
"""

import numpy as np
import pandas as pd
import pytest

from src.data.generator import generate_elasticity_data
from src.models.estimators import (
    OLSLogLogEstimator, PanelFEEstimator, IVEstimator, CrossPriceEstimator,
)
from src.analysis.pricing import OptimalPricingAnalyzer


# ============================================================
# DATA GENERATION
# ============================================================

class TestDataGenerator:
    def setup_method(self):
        self.panel, self.cross_matrix, self.products = generate_elasticity_data(
            n_products=4, n_stores=3, n_weeks=100, seed=42
        )

    def test_panel_shape(self):
        assert len(self.panel) == 4 * 3 * 100

    def test_no_missing_values(self):
        assert not self.panel["quantity"].isna().any()
        assert not self.panel["price"].isna().any()

    def test_positive_prices_quantities(self):
        assert (self.panel["price"] > 0).all()
        assert (self.panel["quantity"] > 0).all()

    def test_cross_matrix_shape(self):
        assert self.cross_matrix.shape == (4, 4)

    def test_diagonal_negative(self):
        # Own-price elasticities should be negative
        for i in range(4):
            assert self.cross_matrix[i, i] < 0

    def test_log_columns_exist(self):
        assert "log_price" in self.panel.columns
        assert "log_quantity" in self.panel.columns

    def test_cost_shock_exists(self):
        assert "cost_shock" in self.panel.columns


# ============================================================
# OLS ESTIMATION
# ============================================================

class TestOLSEstimator:
    def setup_method(self):
        self.panel, _, self.products = generate_elasticity_data(
            n_products=4, n_stores=3, n_weeks=150, seed=42
        )
        self.ols = OLSLogLogEstimator()

    def test_estimates_negative_elasticity(self):
        r = self.ols.estimate(self.panel, "P00")
        assert r.own_elasticity < 0

    def test_elasticity_significant(self):
        r = self.ols.estimate(self.panel, "P00")
        assert r.p_value < 0.05

    def test_reasonable_r_squared(self):
        r = self.ols.estimate(self.panel, "P00")
        assert r.r_squared > 0.1

    def test_estimation_near_true(self):
        true_e = self.products[0].own_elasticity
        r = self.ols.estimate(self.panel, "P00", true_elasticity=true_e)
        # Should be within 0.5 of true value
        assert abs(r.own_elasticity - true_e) < 0.8

    def test_confidence_interval_contains_estimate(self):
        r = self.ols.estimate(self.panel, "P00")
        assert r.ci_lower <= r.own_elasticity <= r.ci_upper


# ============================================================
# PANEL FE ESTIMATION
# ============================================================

class TestPanelFEEstimator:
    def setup_method(self):
        self.panel, _, self.products = generate_elasticity_data(
            n_products=4, n_stores=3, n_weeks=150, seed=42
        )
        self.fe = PanelFEEstimator()

    def test_estimates_negative_elasticity(self):
        r = self.fe.estimate(self.panel, "P00")
        assert r.own_elasticity < 0

    def test_method_label(self):
        r = self.fe.estimate(self.panel, "P00")
        assert "Panel FE" in r.method


# ============================================================
# IV ESTIMATION
# ============================================================

class TestIVEstimator:
    def setup_method(self):
        self.panel, _, self.products = generate_elasticity_data(
            n_products=4, n_stores=3, n_weeks=150, seed=42
        )
        self.iv = IVEstimator()

    def test_estimates_negative_elasticity(self):
        r, diag = self.iv.estimate(self.panel, "P00")
        assert r.own_elasticity < 0

    def test_first_stage_f(self):
        _, diag = self.iv.estimate(self.panel, "P00")
        assert diag.first_stage_f > 0

    def test_diagnostics_populated(self):
        _, diag = self.iv.estimate(self.panel, "P00")
        assert diag.instrument_relevance in ("strong", "weak")
        assert diag.endogeneity in ("detected", "not_detected")


# ============================================================
# CROSS-PRICE ELASTICITY
# ============================================================

class TestCrossPriceEstimator:
    def test_matrix_shape(self):
        panel, true_matrix, products = generate_elasticity_data(
            n_products=4, n_stores=3, n_weeks=100, seed=42
        )
        est = CrossPriceEstimator()
        product_ids = [p.product_id for p in products]
        est_matrix, results = est.estimate(panel, product_ids, true_matrix)
        assert est_matrix.shape == (4, 4)

    def test_own_price_negative(self):
        panel, _, products = generate_elasticity_data(
            n_products=4, n_stores=3, n_weeks=100, seed=42
        )
        est = CrossPriceEstimator()
        product_ids = [p.product_id for p in products]
        est_matrix, _ = est.estimate(panel, product_ids)
        # Diagonal (own-price) should be negative
        for i in range(4):
            assert est_matrix[i, i] < 0


# ============================================================
# OPTIMAL PRICING
# ============================================================

class TestOptimalPricing:
    def setup_method(self):
        _, _, self.products = generate_elasticity_data(
            n_products=4, n_stores=3, n_weeks=100, seed=42
        )
        self.analyzer = OptimalPricingAnalyzer(self.products)

    def test_produces_results(self):
        elasticities = {p.product_id: p.own_elasticity for p in self.products}
        results = self.analyzer.compute_optimal_prices(elasticities)
        assert len(results) == 4

    def test_optimal_price_above_cost(self):
        elasticities = {p.product_id: p.own_elasticity for p in self.products}
        results = self.analyzer.compute_optimal_prices(elasticities)
        for r in results:
            assert r.optimal_price > r.marginal_cost

    def test_profit_uplift_non_negative(self):
        elasticities = {p.product_id: -2.0 for p in self.products}
        results = self.analyzer.compute_optimal_prices(elasticities)
        for r in results:
            assert r.optimal_profit >= r.current_profit * 0.8  # Allow some tolerance

    def test_demand_curve(self):
        prices, quantities = OptimalPricingAnalyzer.compute_demand_curve(10.0, 100, -1.5)
        assert len(prices) == 100
        assert len(quantities) == 100
        assert quantities[0] > quantities[-1]  # Higher price → lower quantity


# ============================================================
# INTEGRATION
# ============================================================

class TestIntegration:
    def test_full_pipeline(self):
        panel, true_matrix, products = generate_elasticity_data(
            n_products=4, n_stores=3, n_weeks=100, seed=42
        )
        product_ids = [p.product_id for p in products]

        # OLS
        ols = OLSLogLogEstimator()
        ols_results = [ols.estimate(panel, pid) for pid in product_ids]
        assert all(r.own_elasticity < 0 for r in ols_results)

        # Cross-price
        cross_est = CrossPriceEstimator()
        est_matrix, _ = cross_est.estimate(panel, product_ids)
        assert est_matrix.shape == (4, 4)

        # Pricing
        elasticities = {r.product_id: r.own_elasticity for r in ols_results}
        analyzer = OptimalPricingAnalyzer(products)
        pricing = analyzer.compute_optimal_prices(elasticities)
        assert len(pricing) == 4
