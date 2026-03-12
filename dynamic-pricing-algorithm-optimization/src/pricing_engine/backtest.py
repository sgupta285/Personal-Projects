from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from pricing_engine.data_generation import expected_units
from pricing_engine.optimizer import recommend_for_row


def run_backtest(test_df: pd.DataFrame, catalog: pd.DataFrame, model, metadata: dict, artifact_dir: Path) -> tuple[pd.DataFrame, dict]:
    catalog_lookup = catalog.set_index("product_id")
    evaluation_df = test_df.copy()
    if len(evaluation_df) > 150:
        step = max(1, len(evaluation_df) // 150)
        evaluation_df = evaluation_df.iloc[::step].head(150).copy()

    rows = []
    for _, row in evaluation_df.iterrows():
        rec = recommend_for_row(row, model, metadata)
        product_meta = catalog_lookup.loc[row["product_id"]]

        actual_units = min(
            expected_units(row, product_meta, float(row["price"])),
            float(row["inventory_level"]),
        )
        optimized_units = min(
            expected_units(row, product_meta, float(rec.recommended_price)),
            float(row["inventory_level"]),
        )

        actual_profit = max(float(row["price"]) - float(row["unit_cost"]), 0.0) * actual_units
        optimized_profit = max(float(rec.recommended_price) - float(row["unit_cost"]), 0.0) * optimized_units
        actual_revenue = float(row["price"]) * actual_units
        optimized_revenue = float(rec.recommended_price) * optimized_units

        rows.append(
            {
                "date": row["date"],
                "product_id": row["product_id"],
                "category": row["category"],
                "channel": row["channel"],
                "current_price": rec.current_price,
                "recommended_price": rec.recommended_price,
                "price_change_pct": rec.price_change_pct,
                "actual_revenue_static": round(float(actual_revenue), 4),
                "actual_revenue_optimized": round(float(optimized_revenue), 4),
                "actual_profit_static": round(float(actual_profit), 4),
                "actual_profit_optimized": round(float(optimized_profit), 4),
                "profit_uplift": round(float(optimized_profit - actual_profit), 4),
                "revenue_uplift": round(float(optimized_revenue - actual_revenue), 4),
                "inventory_level": row["inventory_level"],
            }
        )

    backtest_df = pd.DataFrame(rows)
    summary = {
        "rows_evaluated": int(len(backtest_df)),
        "holdout_rows_available": int(len(test_df)),
        "total_static_revenue": round(float(backtest_df["actual_revenue_static"].sum()), 2),
        "total_optimized_revenue": round(float(backtest_df["actual_revenue_optimized"].sum()), 2),
        "total_static_profit": round(float(backtest_df["actual_profit_static"].sum()), 2),
        "total_optimized_profit": round(float(backtest_df["actual_profit_optimized"].sum()), 2),
        "revenue_uplift_pct": round(
            float(
                (backtest_df["actual_revenue_optimized"].sum() - backtest_df["actual_revenue_static"].sum())
                / max(backtest_df["actual_revenue_static"].sum(), 1e-6)
                * 100
            ),
            2,
        ),
        "profit_uplift_pct": round(
            float(
                (backtest_df["actual_profit_optimized"].sum() - backtest_df["actual_profit_static"].sum())
                / max(backtest_df["actual_profit_static"].sum(), 1e-6)
                * 100
            ),
            2,
        ),
        "recommendation_win_rate": round(float((backtest_df["profit_uplift"] > 0).mean() * 100), 2),
        "avg_price_change_pct": round(float(backtest_df["price_change_pct"].mean()), 2),
    }

    backtest_df.to_csv(artifact_dir / "backtest_rows.csv", index=False)
    (artifact_dir / "backtest_summary.json").write_text(json.dumps(summary, indent=2))
    return backtest_df, summary
