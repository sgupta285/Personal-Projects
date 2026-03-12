from pathlib import Path
import json

import pandas as pd
import plotly.express as px

ROOT = Path(__file__).resolve().parents[1]
features = pd.read_csv(ROOT / "data/processed/customer_features.csv")
metrics = json.loads((ROOT / "artifacts/metrics.json").read_text())
queue = pd.read_csv(ROOT / "artifacts/top_risk_accounts.csv")

print("Rows:", len(features))
print(metrics)

segment_summary = (
    queue.groupby("plan_tier")["churn_probability"]
    .agg(["count", "mean"])
    .sort_values("mean", ascending=False)
    .reset_index()
)
print(segment_summary)

fig = px.histogram(
    features,
    x="days_since_last_activity",
    color="churned_60d",
    nbins=30,
    title="Recency distribution by churn label",
)
fig.show()

fig = px.scatter(
    queue.head(100),
    x="monthly_recurring_revenue",
    y="churn_probability",
    color="recommended_action",
    hover_data=["account_id", "plan_tier", "risk_tier"],
    title="Top risk queue by value",
)
fig.show()
