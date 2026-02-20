"""
Evaluation: walk-forward cross-validation and forecasting metrics.

Walk-forward validation:
  For each window: train on [t-train_days, t], test on [t+1, t+test_days]
  Step forward by step_days and repeat.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import structlog

from src.models.forecasters import BaseForecaster
from src.features.engineer import FeatureEngineer

logger = structlog.get_logger()


@dataclass
class ForecastMetrics:
    mae: float
    rmse: float
    mape: float
    smape: float
    bias: float
    r_squared: float
    under_forecast_pct: float
    over_forecast_pct: float


def compute_metrics(actual: np.ndarray, predicted: np.ndarray) -> ForecastMetrics:
    """Compute comprehensive forecast accuracy metrics."""
    actual = np.array(actual, dtype=float)
    predicted = np.array(predicted, dtype=float)
    n = len(actual)

    residuals = actual - predicted

    mae = np.mean(np.abs(residuals))
    rmse = np.sqrt(np.mean(residuals ** 2))

    # MAPE (exclude zeros)
    nonzero = actual > 0
    mape = np.mean(np.abs(residuals[nonzero]) / actual[nonzero]) * 100 if nonzero.sum() > 0 else 999

    # Symmetric MAPE
    denom = (np.abs(actual) + np.abs(predicted))
    smape_vals = 2 * np.abs(residuals) / np.where(denom > 0, denom, 1)
    smape = np.mean(smape_vals) * 100

    bias = np.mean(residuals)

    # R²
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((actual - np.mean(actual)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    under = np.mean(predicted < actual) * 100
    over = np.mean(predicted > actual) * 100

    return ForecastMetrics(
        mae=round(mae, 2), rmse=round(rmse, 2),
        mape=round(mape, 2), smape=round(smape, 2),
        bias=round(bias, 2), r_squared=round(r2, 4),
        under_forecast_pct=round(under, 1),
        over_forecast_pct=round(over, 1),
    )


@dataclass
class WalkForwardResult:
    window_id: int
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp
    metrics: ForecastMetrics
    actuals: np.ndarray
    predictions: np.ndarray


class WalkForwardValidator:
    """Walk-forward (expanding or rolling window) cross-validation."""

    def __init__(self, train_days=365, test_days=28, step_days=28):
        self.train_days = train_days
        self.test_days = test_days
        self.step_days = step_days

    def validate(
        self,
        df: pd.DataFrame,
        model: BaseForecaster,
        feature_cols: List[str],
        target_col: str = "quantity",
    ) -> List[WalkForwardResult]:
        """
        Run walk-forward validation.

        Args:
            df: DataFrame with date column, features, and target
            model: Forecaster to evaluate
            feature_cols: Feature column names
            target_col: Target column name

        Returns:
            List of WalkForwardResult for each window
        """
        df = df.sort_values("date").reset_index(drop=True)
        dates = df["date"].values
        n = len(df)
        results = []
        window_id = 0

        start = self.train_days
        while start + self.test_days <= n:
            train_idx = slice(max(0, start - self.train_days), start)
            test_idx = slice(start, min(start + self.test_days, n))

            X_train = df.loc[train_idx, feature_cols]
            y_train = df.loc[train_idx, target_col]
            X_test = df.loc[test_idx, feature_cols]
            y_test = df.loc[test_idx, target_col].values

            # Add dates for Prophet
            dates_train = df.loc[train_idx, "date"]

            try:
                model.fit(X_train, y_train, dates_train=dates_train)
                preds = model.predict(df.loc[test_idx])
            except Exception as e:
                logger.warning("wf_window_failed", window=window_id, error=str(e))
                preds = np.full(len(y_test), y_train.mean())

            metrics = compute_metrics(y_test, preds)

            results.append(WalkForwardResult(
                window_id=window_id,
                train_start=pd.Timestamp(dates[train_idx][0]),
                train_end=pd.Timestamp(dates[train_idx][-1]),
                test_start=pd.Timestamp(dates[test_idx][0]),
                test_end=pd.Timestamp(dates[test_idx][-1]),
                metrics=metrics,
                actuals=y_test,
                predictions=preds,
            ))

            window_id += 1
            start += self.step_days

        logger.info("walk_forward_complete", model=model.name, windows=len(results))
        return results


def summarize_walk_forward(results: List[WalkForwardResult]) -> Dict:
    """Aggregate walk-forward results across all windows."""
    if not results:
        return {}

    maes = [r.metrics.mae for r in results]
    rmses = [r.metrics.rmse for r in results]
    mapes = [r.metrics.mape for r in results]

    return {
        "n_windows": len(results),
        "mae_mean": round(np.mean(maes), 2),
        "mae_std": round(np.std(maes), 2),
        "rmse_mean": round(np.mean(rmses), 2),
        "rmse_std": round(np.std(rmses), 2),
        "mape_mean": round(np.mean(mapes), 2),
        "mape_std": round(np.std(mapes), 2),
        "best_window_mape": round(min(mapes), 2),
        "worst_window_mape": round(max(mapes), 2),
    }


def print_metrics_table(model_results: Dict[str, Dict]):
    """Print comparison table across models."""
    print(f"\n{'='*75}")
    print(f"  WALK-FORWARD VALIDATION RESULTS")
    print(f"{'='*75}")
    print(f"  {'Model':<15} {'MAE':>8} {'RMSE':>8} {'MAPE%':>8} "
          f"{'Best%':>8} {'Worst%':>8} {'Windows':>8}")
    print(f"  {'-'*70}")

    for model_name, summary in model_results.items():
        print(f"  {model_name:<15} {summary['mae_mean']:>8.1f} {summary['rmse_mean']:>8.1f} "
              f"{summary['mape_mean']:>7.1f}% {summary['best_window_mape']:>7.1f}% "
              f"{summary['worst_window_mape']:>7.1f}% {summary['n_windows']:>8}")
    print(f"{'='*75}\n")
