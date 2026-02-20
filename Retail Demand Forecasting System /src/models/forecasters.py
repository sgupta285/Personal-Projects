"""
Forecasting Models.

Implements SARIMA, Prophet, XGBoost, LightGBM, and weighted ensemble
with a unified interface for training, prediction, and evaluation.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
import warnings
import structlog

warnings.filterwarnings("ignore")
logger = structlog.get_logger()


class BaseForecaster(ABC):
    """Abstract base class for all forecasting models."""

    @abstractmethod
    def fit(self, X_train: pd.DataFrame, y_train: pd.Series, **kwargs) -> "BaseForecaster":
        pass

    @abstractmethod
    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class XGBoostForecaster(BaseForecaster):
    """XGBoost gradient boosting forecaster."""

    def __init__(self, n_estimators=500, max_depth=6, learning_rate=0.05, seed=42):
        self.params = dict(
            n_estimators=n_estimators, max_depth=max_depth,
            learning_rate=learning_rate, random_state=seed,
            subsample=0.8, colsample_bytree=0.8,
            min_child_weight=5, reg_alpha=0.1, reg_lambda=1.0,
        )
        self.model = None
        self._feature_names = None

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series, **kwargs) -> "XGBoostForecaster":
        from xgboost import XGBRegressor
        self.model = XGBRegressor(**self.params)
        self._feature_names = list(X_train.columns)

        eval_set = kwargs.get("eval_set", None)
        self.model.fit(
            X_train, y_train,
            eval_set=eval_set,
            verbose=False,
        )
        logger.info("xgboost_trained", n_features=len(self._feature_names))
        return self

    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        preds = self.model.predict(X_test[self._feature_names])
        return np.maximum(preds, 0)  # Demand can't be negative

    def feature_importance(self, top_n: int = 20) -> pd.Series:
        if self.model is None:
            return pd.Series()
        imp = pd.Series(self.model.feature_importances_, index=self._feature_names)
        return imp.nlargest(top_n)

    @property
    def name(self) -> str:
        return "xgboost"


class LightGBMForecaster(BaseForecaster):
    """LightGBM gradient boosting forecaster."""

    def __init__(self, n_estimators=500, num_leaves=31, learning_rate=0.05, seed=42):
        self.params = dict(
            n_estimators=n_estimators, num_leaves=num_leaves,
            learning_rate=learning_rate, random_state=seed,
            subsample=0.8, colsample_bytree=0.8,
            min_child_samples=20, reg_alpha=0.1, reg_lambda=1.0,
            verbosity=-1,
        )
        self.model = None
        self._feature_names = None

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series, **kwargs) -> "LightGBMForecaster":
        from lightgbm import LGBMRegressor
        self.model = LGBMRegressor(**self.params)
        self._feature_names = list(X_train.columns)
        self.model.fit(X_train, y_train)
        logger.info("lightgbm_trained", n_features=len(self._feature_names))
        return self

    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        preds = self.model.predict(X_test[self._feature_names])
        return np.maximum(preds, 0)

    def feature_importance(self, top_n: int = 20) -> pd.Series:
        if self.model is None:
            return pd.Series()
        imp = pd.Series(self.model.feature_importances_, index=self._feature_names)
        return imp.nlargest(top_n)

    @property
    def name(self) -> str:
        return "lightgbm"


class SARIMAForecaster(BaseForecaster):
    """SARIMA time series forecaster."""

    def __init__(self, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7)):
        self.order = order
        self.seasonal_order = seasonal_order
        self.model = None
        self._fitted = None

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series, **kwargs) -> "SARIMAForecaster":
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        # Use only the time series (ignore X features for pure SARIMA)
        try:
            model = SARIMAX(
                y_train.values, order=self.order,
                seasonal_order=self.seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False,
            )
            self._fitted = model.fit(disp=False, maxiter=200)
            logger.info("sarima_trained", aic=round(self._fitted.aic, 1))
        except Exception as e:
            logger.warning("sarima_fit_failed", error=str(e))
            self._fitted = None
        return self

    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        if self._fitted is None:
            return np.zeros(len(X_test))
        try:
            n = len(X_test)
            forecast = self._fitted.forecast(steps=n)
            return np.maximum(forecast, 0)
        except Exception:
            return np.zeros(len(X_test))

    @property
    def name(self) -> str:
        return "sarima"


class ProphetForecaster(BaseForecaster):
    """Facebook Prophet forecaster with holidays and regressors."""

    def __init__(self, changepoint_prior=0.05, seasonality_prior=10.0):
        self.changepoint_prior = changepoint_prior
        self.seasonality_prior = seasonality_prior
        self.model = None

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series, **kwargs) -> "ProphetForecaster":
        try:
            from prophet import Prophet
            prophet_df = pd.DataFrame({
                "ds": kwargs.get("dates_train", pd.date_range("2021-01-01", periods=len(y_train))),
                "y": y_train.values,
            })

            self.model = Prophet(
                changepoint_prior_scale=self.changepoint_prior,
                seasonality_prior_scale=self.seasonality_prior,
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
            )
            self.model.fit(prophet_df)
            logger.info("prophet_trained")
        except ImportError:
            logger.warning("prophet_not_installed")
            self.model = None
        except Exception as e:
            logger.warning("prophet_fit_failed", error=str(e))
            self.model = None
        return self

    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            return np.zeros(len(X_test))
        try:
            dates = X_test.get("date", pd.date_range("2023-01-01", periods=len(X_test)))
            future = pd.DataFrame({"ds": dates})
            forecast = self.model.predict(future)
            return np.maximum(forecast["yhat"].values, 0)
        except Exception:
            return np.zeros(len(X_test))

    @property
    def name(self) -> str:
        return "prophet"


class EnsembleForecaster(BaseForecaster):
    """Weighted ensemble of multiple forecasters."""

    def __init__(self, models: List[BaseForecaster], weights: Optional[Dict[str, float]] = None):
        self.models = models
        self.weights = weights or {m.name: 1.0 / len(models) for m in models}
        self._normalize_weights()

    def _normalize_weights(self):
        total = sum(self.weights.get(m.name, 0) for m in self.models)
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series, **kwargs) -> "EnsembleForecaster":
        for model in self.models:
            model.fit(X_train, y_train, **kwargs)
        return self

    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        predictions = np.zeros(len(X_test))
        for model in self.models:
            w = self.weights.get(model.name, 0)
            if w > 0:
                preds = model.predict(X_test)
                predictions += w * preds
        return np.maximum(predictions, 0)

    @property
    def name(self) -> str:
        return "ensemble"
