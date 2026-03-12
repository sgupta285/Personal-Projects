from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.io as pio


def export_dashboard_assets(
    recommendations: pd.DataFrame,
    backtest_df: pd.DataFrame,
    backtest_summary: dict,
    sample_curve: pd.DataFrame,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    uplift_by_category = (
        backtest_df.groupby("category")["profit_uplift"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    fig1 = px.bar(
        uplift_by_category,
        x="category",
        y="profit_uplift",
        title="Backtest gross profit uplift by category",
    )

    fig2 = px.scatter(
        recommendations.head(120),
        x="current_price",
        y="recommended_price",
        color="category",
        hover_data=["product_id", "channel", "expected_profit_uplift_pct"],
        title="Recommended price versus current price",
    )

    fig3 = px.line(
        sample_curve,
        x="candidate_price",
        y=["expected_revenue", "expected_profit"],
        title="Sample price sensitivity curve",
    )

    figures_html = "\n".join(
        [
            pio.to_html(fig1, include_plotlyjs="cdn", full_html=False),
            pio.to_html(fig2, include_plotlyjs=False, full_html=False),
            pio.to_html(fig3, include_plotlyjs=False, full_html=False),
        ]
    )

    metrics_html = f"""
    <div class="cards">
      <div class="card"><h3>Profit uplift</h3><p>{backtest_summary['profit_uplift_pct']}%</p></div>
      <div class="card"><h3>Revenue uplift</h3><p>{backtest_summary['revenue_uplift_pct']}%</p></div>
      <div class="card"><h3>Win rate</h3><p>{backtest_summary['recommendation_win_rate']}%</p></div>
      <div class="card"><h3>Average price change</h3><p>{backtest_summary['avg_price_change_pct']}%</p></div>
    </div>
    """

    table_html = recommendations.head(25).to_html(index=False, classes="recommendation-table")

    html = f"""
    <html>
    <head>
      <title>Dynamic Pricing Dashboard</title>
      <style>
        body {{ font-family: Arial, sans-serif; margin: 24px; background: #f8fafc; color: #0f172a; }}
        .cards {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; }}
        .card {{ background: white; border-radius: 12px; padding: 16px; min-width: 180px; box-shadow: 0 2px 8px rgba(15,23,42,0.08); }}
        .recommendation-table {{ background: white; border-collapse: collapse; width: 100%; font-size: 13px; }}
        .recommendation-table th, .recommendation-table td {{ border: 1px solid #e2e8f0; padding: 8px; }}
      </style>
    </head>
    <body>
      <h1>Dynamic Pricing Dashboard</h1>
      <p>Offline dashboard generated from the latest model artifacts and backtest outputs.</p>
      {metrics_html}
      {figures_html}
      <h2>Top recommendation queue</h2>
      {table_html}
    </body>
    </html>
    """
    (output_dir / "pricing_dashboard.html").write_text(html)

    plt.figure(figsize=(10, 5))
    sample = recommendations.head(30).copy()
    plt.bar(sample["product_id"], sample["expected_profit_uplift_pct"])
    plt.xticks(rotation=90)
    plt.title("Profit uplift for top recommendation queue")
    plt.tight_layout()
    plt.savefig(output_dir / "recommendation_snapshot.png", dpi=150)
    plt.close()

    sample_curve.to_csv(output_dir / "sample_curve_snapshot.csv", index=False)
