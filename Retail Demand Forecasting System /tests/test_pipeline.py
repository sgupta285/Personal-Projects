"""
Test suite for Retail Demand Forecasting System.
"""

import numpy as np
import pandas as pd
import pytest

from src.data.generator import generate_retail_data, aggregate_daily
from src.features.engineer import FeatureEngineer, FeatureConfig
from src.models.forecasters import (
    XGBoostForecaster, LightGBMForecaster, SARIMAForecaster, EnsembleForecaster,
)
from src.evaluation.validator import compute_metrics, WalkForwardValidator


# ============================================================
# DATA GENERATION
# ============================================================

class TestDataGenerator:
    def test_generates_correct_shape(self):
        sales, stores, products = generate_retail_data(n_stores=2, n_products=3, n_days=30)
        assert len(sales) == 2 * 3 * 30  # stores × products × days
        assert len(stores) == 2
        assert len(products) == 3

    def test_no_nan_values(self):
        sales, _, _ = generate_retail_data(n_stores=2, n_products=5, n_days=100)
        assert not sales["quantity"].isna().any()
        assert not sales["revenue"].isna().any()

    def test_no_negative_quantities(self):
        sales, _, _ = generate_retail_data(n_stores=3, n_products=5, n_days=200)
        assert (sales["quantity"] >= 0).all()

    def test_promotions_increase_demand(self):
        sales, _, _ = generate_retail_data(n_stores=5, n_products=10, n_days=500, seed=42)
        promo_demand = sales[sales["is_promotion"]]["quantity"].mean()
        normal_demand = sales[~sales["is_promotion"]]["quantity"].mean()
        assert promo_demand > normal_demand

    def test_aggregate_daily(self):
        sales, _, _ = generate_retail_data(n_stores=2, n_products=3, n_days=30)
        daily = aggregate_daily(sales, level="store")
        # Should have 2 stores × 30 days = 60 rows
        assert len(daily) == 60


# ============================================================
# FEATURE ENGINEERING
# ============================================================

class TestFeatureEngineer:
    def setup_method(self):
        np.random.seed(42)
        dates = pd.date_range("2021-01-01", periods=200)
        self.df = pd.DataFrame({
            "date": dates,
            "quantity": np.random.poisson(100, 200),
            "discount_pct": np.random.uniform(0, 20, 200),
            "is_promotion": np.random.choice([True, False], 200),
            "is_holiday": np.random.choice([True, False], 200, p=[0.05, 0.95]),
            "temperature": 50 + 20 * np.sin(np.linspace(0, 4 * np.pi, 200)) + np.random.randn(200) * 5,
        })

    def test_builds_features(self):
        fe = FeatureEngineer()
        featured = fe.build_features(self.df)
        assert len(featured) > 0
        assert "lag_1" in featured.columns
        assert "roll_mean_7" in featured.columns
        assert "sin_weekly_1" in featured.columns

    def test_no_nans_after_build(self):
        fe = FeatureEngineer()
        featured = fe.build_features(self.df)
        feature_cols = FeatureEngineer.get_feature_columns(featured)
        # Features used for ML should have no NaN
        for col in feature_cols:
            nan_count = featured[col].isna().sum()
            assert nan_count == 0, f"Column {col} has {nan_count} NaN values"

    def test_feature_columns_excludes_target(self):
        fe = FeatureEngineer()
        featured = fe.build_features(self.df)
        feature_cols = FeatureEngineer.get_feature_columns(featured)
        assert "quantity" not in feature_cols
        assert "date" not in feature_cols

    def test_lag_features_correct(self):
        fe = FeatureEngineer(FeatureConfig(lag_days=[1], rolling_windows=[7], ewm_spans=[7]))
        featured = fe.build_features(self.df)
        # lag_1 should be previous day's quantity
        idx = 10  # Arbitrary valid index
        assert featured.iloc[idx]["lag_1"] == self.df.iloc[idx + fe.cfg.rolling_windows[0] - 1]["quantity"]


# ============================================================
# MODELS
# ============================================================

class TestModels:
    def setup_method(self):
        np.random.seed(42)
        n = 300
        x1 = np.random.randn(n)
        x2 = np.random.randn(n)
        y = 50 + 3 * x1 - 2 * x2 + np.random.randn(n) * 5
        self.X_train = pd.DataFrame({"x1": x1[:200], "x2": x2[:200]})
        self.y_train = pd.Series(y[:200])
        self.X_test = pd.DataFrame({"x1": x1[200:], "x2": x2[200:]})
        self.y_test = y[200:]

    def test_xgboost_trains_and_predicts(self):
        model = XGBoostForecaster(n_estimators=50)
        model.fit(self.X_train, self.y_train)
        preds = model.predict(self.X_test)
        assert len(preds) == len(self.X_test)
        assert (preds >= 0).all()

    def test_lightgbm_trains_and_predicts(self):
        model = LightGBMForecaster(n_estimators=50)
        model.fit(self.X_train, self.y_train)
        preds = model.predict(self.X_test)
        assert len(preds) == len(self.X_test)

    def test_xgboost_feature_importance(self):
        model = XGBoostForecaster(n_estimators=50)
        model.fit(self.X_train, self.y_train)
        imp = model.feature_importance()
        assert len(imp) > 0
        assert imp.sum() > 0

    def test_ensemble(self):
        m1 = XGBoostForecaster(n_estimators=30)
        m2 = LightGBMForecaster(n_estimators=30)
        m1.fit(self.X_train, self.y_train)
        m2.fit(self.X_train, self.y_train)

        ens = EnsembleForecaster([m1, m2], {"xgboost": 0.6, "lightgbm": 0.4})
        preds = ens.predict(self.X_test)
        assert len(preds) == len(self.X_test)

    def test_sarima_basic(self):
        model = SARIMAForecaster(order=(1, 0, 0), seasonal_order=(0, 0, 0, 1))
        model.fit(self.X_train, self.y_train)
        preds = model.predict(self.X_test)
        assert len(preds) == len(self.X_test)


# ============================================================
# EVALUATION
# ============================================================

class TestEvaluation:
    def test_compute_metrics(self):
        actual = np.array([100, 200, 150, 300, 250])
        pred = np.array([110, 190, 160, 280, 240])
        m = compute_metrics(actual, pred)
        assert m.mae > 0
        assert m.rmse >= m.mae
        assert 0 < m.mape < 100
        assert -100 < m.bias < 100

    def test_perfect_forecast(self):
        actual = np.array([100, 200, 150])
        m = compute_metrics(actual, actual)
        assert m.mae == 0
        assert m.rmse == 0
        assert m.mape == 0
        assert m.r_squared == 1.0

    def test_walk_forward_produces_results(self):
        np.random.seed(42)
        n = 500
        df = pd.DataFrame({
            "date": pd.date_range("2021-01-01", periods=n),
            "quantity": np.random.poisson(100, n).astype(float),
            "x1": np.random.randn(n),
            "x2": np.random.randn(n),
        })

        model = XGBoostForecaster(n_estimators=30)
        wf = WalkForwardValidator(train_days=200, test_days=30, step_days=30)
        results = wf.validate(df, model, ["x1", "x2"])

        assert len(results) > 0
        for r in results:
            assert r.metrics.mae >= 0
            assert len(r.actuals) == len(r.predictions)


# ============================================================
# INTEGRATION
# ============================================================

class TestIntegration:
    def test_full_pipeline_single_store(self):
        """End-to-end: data → features → model → metrics."""
        sales, _, _ = generate_retail_data(n_stores=1, n_products=5, n_days=400, seed=42)
        daily = aggregate_daily(sales, level="store")
        store_data = daily[daily["store_id"] == daily["store_id"].iloc[0]]

        fe = FeatureEngineer()
        featured = fe.build_features(store_data)
        feature_cols = FeatureEngineer.get_feature_columns(featured)

        split = int(len(featured) * 0.7)
        train = featured.iloc[:split]
        test = featured.iloc[split:]

        model = XGBoostForecaster(n_estimators=50)
        model.fit(train[feature_cols], train["quantity"])
        preds = model.predict(test[feature_cols])

        m = compute_metrics(test["quantity"].values, preds)
        assert m.mape < 50  # Should be reasonable on synthetic data
        assert m.r_squared > 0  # Should explain some variance
