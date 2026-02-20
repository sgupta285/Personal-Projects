"""
Retail Demand Forecasting Pipeline.

End-to-end: synthetic data generation → feature engineering → model training →
walk-forward validation → model comparison → ensemble.

Usage: python -m src.main
"""

import os
import time
import numpy as np
import pandas as pd
import structlog
from typing import Dict

from src.config import config
from src.data.generator import generate_retail_data, aggregate_daily
from src.features.engineer import FeatureEngineer
from src.models.forecasters import (
    XGBoostForecaster, LightGBMForecaster,
    SARIMAForecaster, EnsembleForecaster,
)
from src.evaluation.validator import (
    WalkForwardValidator, compute_metrics,
    summarize_walk_forward, print_metrics_table,
)
from src.utils.visualization import (
    plot_forecast_vs_actual, plot_feature_importance,
    plot_walk_forward_mape, plot_residuals, plot_demand_decomposition,
)

logger = structlog.get_logger()


def main():
    """Run full demand forecasting pipeline."""
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(30),
    )

    output_dir = config.output_dir
    os.makedirs(output_dir, exist_ok=True)
    t0 = time.perf_counter()

    print(f"\n{'='*65}")
    print(f"  RETAIL DEMAND FORECASTING SYSTEM")
    print(f"{'='*65}")
    print(f"  Stores: {config.data.n_stores}  |  Products: {config.data.n_products}")
    print(f"  Period: {config.data.n_days} days (~{config.data.n_days/365:.1f} years)")
    print(f"{'='*65}\n")

    # ── Step 1: Generate Data ──
    print("1. Generating synthetic retail data...")
    sales_df, stores_df, products_df = generate_retail_data(
        n_stores=config.data.n_stores,
        n_products=config.data.n_products,
        n_days=config.data.n_days,
        start_date=config.data.start_date,
        seed=config.data.seed,
    )
    print(f"   ✓ {len(sales_df):,} rows ({config.data.n_stores} stores × "
          f"{config.data.n_products} products × {config.data.n_days} days)")

    # Aggregate to store-level daily for modeling demo
    daily_df = aggregate_daily(sales_df, level="store")
    print(f"   ✓ Aggregated to {len(daily_df):,} store-day records")

    # Pick one store for single-series demo
    demo_store = daily_df["store_id"].unique()[0]
    series = daily_df[daily_df["store_id"] == demo_store].copy()
    print(f"   ✓ Demo store: {demo_store} ({len(series)} days)")

    # Plot decomposition
    plot_demand_decomposition(sales_df.loc[sales_df["store_id"] == demo_store], output_dir)
    print(f"   ✓ Saved: {output_dir}/demand_decomposition.png")

    # ── Step 2: Feature Engineering ──
    print("\n2. Engineering features...")
    fe = FeatureEngineer(config.features)
    featured = fe.build_features(series)
    feature_cols = FeatureEngineer.get_feature_columns(featured)
    print(f"   ✓ {len(feature_cols)} features, {len(featured)} samples")

    # ── Step 3: Train/Test Split ──
    n = len(featured)
    train_end = int(n * config.data.train_pct)
    val_end = int(n * (config.data.train_pct + config.data.val_pct))

    train = featured.iloc[:train_end]
    val = featured.iloc[train_end:val_end]
    test = featured.iloc[val_end:]

    print(f"\n3. Data split:")
    print(f"   Train: {len(train)} days ({train['date'].min().date()} → {train['date'].max().date()})")
    print(f"   Val:   {len(val)} days ({val['date'].min().date()} → {val['date'].max().date()})")
    print(f"   Test:  {len(test)} days ({test['date'].min().date()} → {test['date'].max().date()})")

    # ── Step 4: Train Models ──
    print("\n4. Training models...")

    X_train = train[feature_cols]
    y_train = train["quantity"]
    X_val = val[feature_cols]
    y_val = val["quantity"]

    models = {
        "xgboost": XGBoostForecaster(
            n_estimators=config.model.xgb_n_estimators,
            max_depth=config.model.xgb_max_depth,
            learning_rate=config.model.xgb_learning_rate,
        ),
        "lightgbm": LightGBMForecaster(
            n_estimators=config.model.lgb_n_estimators,
            num_leaves=config.model.lgb_num_leaves,
            learning_rate=config.model.lgb_learning_rate,
        ),
        "sarima": SARIMAForecaster(
            order=config.model.sarima_order,
            seasonal_order=config.model.sarima_seasonal,
        ),
    }

    for name, model in models.items():
        t_start = time.perf_counter()
        model.fit(X_train, y_train, dates_train=train["date"])
        elapsed = time.perf_counter() - t_start
        print(f"   ✓ {name}: trained in {elapsed:.1f}s")

    # Feature importance
    for name in ["xgboost", "lightgbm"]:
        imp = models[name].feature_importance(top_n=20)
        plot_feature_importance(imp, name, output_dir)
        print(f"   ✓ Saved: {output_dir}/feature_importance_{name}.png")

    # ── Step 5: Validation Set Evaluation ──
    print("\n5. Validation set evaluation:")
    val_results = {}
    for name, model in models.items():
        preds = model.predict(val)
        metrics = compute_metrics(y_val.values, preds)
        val_results[name] = metrics
        print(f"   {name:<12} MAE={metrics.mae:>8.1f}  RMSE={metrics.rmse:>8.1f}  "
              f"MAPE={metrics.mape:>6.1f}%  R²={metrics.r_squared:.3f}")

    # ── Step 6: Build Ensemble ──
    print("\n6. Building ensemble...")
    # Weight by inverse MAPE on validation set
    mapes = {name: max(m.mape, 0.1) for name, m in val_results.items()}
    inv_mape = {k: 1.0 / v for k, v in mapes.items()}
    total = sum(inv_mape.values())
    ensemble_weights = {k: round(v / total, 3) for k, v in inv_mape.items()}
    print(f"   Weights: {ensemble_weights}")

    ensemble = EnsembleForecaster(list(models.values()), ensemble_weights)
    ens_preds = ensemble.predict(val)
    ens_metrics = compute_metrics(y_val.values, ens_preds)
    print(f"   ensemble     MAE={ens_metrics.mae:>8.1f}  RMSE={ens_metrics.rmse:>8.1f}  "
          f"MAPE={ens_metrics.mape:>6.1f}%  R²={ens_metrics.r_squared:.3f}")

    # ── Step 7: Walk-Forward Validation ──
    print("\n7. Walk-forward validation...")
    wf = WalkForwardValidator(
        train_days=config.model.wf_train_days,
        test_days=config.model.wf_test_days,
        step_days=config.model.wf_step_days,
    )

    wf_model_results = {}
    wf_summaries = {}

    # Run XGBoost and LightGBM through walk-forward (skip SARIMA/Prophet for speed)
    for name in ["xgboost", "lightgbm"]:
        results = wf.validate(featured, models[name], feature_cols)
        wf_model_results[name] = results
        wf_summaries[name] = summarize_walk_forward(results)

    print_metrics_table(wf_summaries)
    plot_walk_forward_mape(wf_model_results, output_dir)
    print(f"   ✓ Saved: {output_dir}/wf_mape.png")

    # ── Step 8: Test Set Final Evaluation ──
    print("\n8. Final test set evaluation:")
    test_results = {}
    for name, model in list(models.items()) + [("ensemble", ensemble)]:
        preds = model.predict(test)
        metrics = compute_metrics(test["quantity"].values, preds)
        test_results[name] = {"metrics": metrics, "predictions": preds}
        print(f"   {name:<12} MAE={metrics.mae:>8.1f}  RMSE={metrics.rmse:>8.1f}  "
              f"MAPE={metrics.mape:>6.1f}%  R²={metrics.r_squared:.3f}  "
              f"Bias={metrics.bias:>+.1f}")

    # Plot forecasts
    for name in ["xgboost", "ensemble"]:
        r = test_results[name]
        plot_forecast_vs_actual(
            test["date"].values, test["quantity"].values,
            r["predictions"], name, output_dir,
        )
        plot_residuals(test["quantity"].values, r["predictions"], name, output_dir)
        print(f"   ✓ Saved: {output_dir}/forecast_{name}.png, residuals_{name}.png")

    # ── Step 9: Export ──
    print("\n9. Exporting results...")
    # Save test predictions
    export_df = test[["date", "quantity"]].copy()
    for name, r in test_results.items():
        export_df[f"pred_{name}"] = r["predictions"]
    export_df.to_csv(f"{output_dir}/predictions.csv", index=False)

    # Save summary
    summary = {name: {
        "mae": r["metrics"].mae, "rmse": r["metrics"].rmse,
        "mape": r["metrics"].mape, "r_squared": r["metrics"].r_squared,
        "bias": r["metrics"].bias,
    } for name, r in test_results.items()}
    pd.DataFrame(summary).T.to_csv(f"{output_dir}/model_comparison.csv")
    print(f"   ✓ Saved: {output_dir}/predictions.csv, model_comparison.csv")

    elapsed = time.perf_counter() - t0
    print(f"\n{'='*65}")
    print(f"  PIPELINE COMPLETE — {elapsed:.1f}s total")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
