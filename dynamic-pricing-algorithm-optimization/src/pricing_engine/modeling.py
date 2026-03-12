from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

from pricing_engine.features import TARGET_COLUMN, model_input_frame


def wmape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    denominator = np.sum(np.abs(y_true))
    return float(np.sum(np.abs(y_true - y_pred)) / denominator) if denominator else 0.0


def build_model(random_state: int = 42) -> XGBRegressor:
    return XGBRegressor(
        n_estimators=220,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=1.8,
        min_child_weight=2,
        objective="reg:squarederror",
        random_state=random_state,
        n_jobs=1,
        verbosity=0,
    )


def train_model(feature_df: pd.DataFrame, artifact_dir: Path) -> tuple[XGBRegressor, dict, pd.DataFrame]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    frame = feature_df.copy().sort_values("date")
    split_date = frame["date"].sort_values().unique()[-28]
    train_df = frame[frame["date"] < split_date].copy()
    test_df = frame[frame["date"] >= split_date].copy()

    X_train = model_input_frame(train_df)
    y_train = train_df[TARGET_COLUMN].astype(float)
    X_test = model_input_frame(test_df)
    y_test = test_df[TARGET_COLUMN].astype(float)
    X_test = X_test.reindex(columns=X_train.columns, fill_value=0)

    model = build_model()
    model.fit(X_train, y_train)

    pred_test = np.maximum(model.predict(X_test), 0)
    metrics = {
        "mae": float(mean_absolute_error(y_test, pred_test)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, pred_test))),
        "r2": float(r2_score(y_test, pred_test)),
        "wmape": float(wmape(y_test.to_numpy(), pred_test)),
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
    }

    metadata = {
        "feature_columns": list(X_train.columns),
        "objective": "gross_profit",
        "target": TARGET_COLUMN,
        "train_split_last_days": 28,
    }

    model.save_model(artifact_dir / "model.json")
    (artifact_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (artifact_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    feature_importance = (
        pd.Series(model.feature_importances_, index=X_train.columns)
        .sort_values(ascending=False)
        .head(20)
        .reset_index()
    )
    feature_importance.columns = ["feature", "importance"]
    feature_importance.to_csv(artifact_dir / "feature_importance.csv", index=False)

    return model, metadata, test_df
