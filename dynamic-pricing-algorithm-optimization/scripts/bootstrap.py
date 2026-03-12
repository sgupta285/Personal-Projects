from pathlib import Path

import pandas as pd

from pricing_engine.backtest import run_backtest
from pricing_engine.config import settings
from pricing_engine.data_generation import build_product_catalog, generate_transactions, save_catalog, save_transactions
from pricing_engine.features import build_feature_table, save_feature_table
from pricing_engine.modeling import train_model
from pricing_engine.optimizer import price_curve, recommend_for_row
from pricing_engine.reporting import export_dashboard_assets
from pricing_engine.storage import seed_database


def main() -> None:
    settings.ensure_directories()

    catalog = build_product_catalog(seed=settings.random_seed)
    transactions = generate_transactions(catalog, seed=settings.random_seed)
    features = build_feature_table(transactions)

    save_catalog(catalog, settings.raw_catalog_path)
    save_transactions(transactions, settings.raw_transactions_path)
    save_feature_table(features, settings.processed_feature_path)
    seed_database(catalog, transactions, features, settings.database_path)

    model, metadata, test_df = train_model(features, settings.artifact_dir)
    backtest_df, backtest_summary = run_backtest(test_df, catalog, model, metadata, settings.artifact_dir)

    latest_rows = (
        features.sort_values("date")
        .groupby(["product_id", "channel"], as_index=False)
        .tail(1)
        .sort_values(["inventory_pressure", "price"], ascending=[False, False])
    )
    recommendations = []
    for _, row in latest_rows.iterrows():
        recommendation = recommend_for_row(row, model, metadata)
        recommendations.append(
            {
                "product_id": recommendation.product_id,
                "category": row["category"],
                "channel": row["channel"],
                "current_price": recommendation.current_price,
                "recommended_price": recommendation.recommended_price,
                "price_change_pct": recommendation.price_change_pct,
                "expected_profit_uplift_pct": recommendation.expected_profit_uplift_pct,
                "expected_profit_current": recommendation.expected_profit_current,
                "expected_profit_recommended": recommendation.expected_profit_recommended,
                "inventory_pressure": round(float(row["inventory_pressure"]), 4),
                "competitor_price": float(row["competitor_price"]),
                "guardrail_min_price": recommendation.guardrails["min_price"],
                "guardrail_max_price": recommendation.guardrails["max_price"],
                "reason_1": recommendation.explanation[0] if recommendation.explanation else "",
                "reason_2": recommendation.explanation[1] if len(recommendation.explanation) > 1 else "",
            }
        )
    rec_df = pd.DataFrame(recommendations).sort_values(
        ["expected_profit_uplift_pct", "inventory_pressure"], ascending=[False, False]
    )
    rec_df.to_csv(settings.artifact_dir / "top_recommendations.csv", index=False)

    elasticity_report = (
        features.assign(implied_elasticity=-(features["units_sold"] + 1).div(features["price_index_vs_base"] + 0.01))
        .groupby("category")
        .agg(
            avg_price=("price", "mean"),
            avg_units=("units_sold", "mean"),
            avg_inventory_pressure=("inventory_pressure", "mean"),
            avg_competitor_gap=("competitor_gap_pct", "mean"),
        )
        .reset_index()
    )
    elasticity_report.to_csv(settings.artifact_dir / "elasticity_report.csv", index=False)

    sample_row = latest_rows.iloc[0]
    sample_curve, _ = price_curve(sample_row, model, metadata)
    sample_curve.to_csv(settings.artifact_dir / "sample_price_curve.csv", index=False)

    export_dashboard_assets(rec_df, backtest_df, backtest_summary, sample_curve, Path("dashboard/output"))

    sample_payload = sample_row.to_dict()
    sample_payload["date"] = pd.to_datetime(sample_payload["date"]).date().isoformat()
    (settings.root_dir / "data/sample_request.json").write_text(pd.Series(sample_payload).to_json(indent=2))

    print("Bootstrap complete. Outputs written to artifacts/, data/, and dashboard/output/.")


if __name__ == "__main__":
    main()
