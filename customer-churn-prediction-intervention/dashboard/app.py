from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
FEATURE_PATH = ROOT / "data/processed/customer_features.csv"

st.set_page_config(page_title="Churn Intelligence", layout="wide")
st.title("Customer Churn Prediction & Intervention")

if not (ARTIFACT_DIR / "metrics.json").exists():
    st.warning("Artifacts are missing. Run `make bootstrap` first.")
    st.stop()

metrics = json.loads((ARTIFACT_DIR / "metrics.json").read_text())
queue = pd.read_csv(ARTIFACT_DIR / "top_risk_accounts.csv")
features = pd.read_csv(FEATURE_PATH)
confusion = json.loads((ARTIFACT_DIR / "confusion_matrix.json").read_text())

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("ROC-AUC", f"{metrics['roc_auc']:.3f}")
col2.metric("PR-AUC", f"{metrics['pr_auc']:.3f}")
col3.metric("Precision@10%", f"{metrics['precision_at_10_pct']:.3f}")
col4.metric("Recall@10%", f"{metrics['recall_at_10_pct']:.3f}")
col5.metric("Simulated uplift", f"{metrics['simulated_retention_uplift']:.1f}%")

left, right = st.columns([1.15, 1.0])
with left:
    st.subheader("Top risk intervention queue")
    st.dataframe(queue.head(50), use_container_width=True)

with right:
    st.subheader("Confusion matrix")
    cm_df = pd.DataFrame(confusion["matrix"], index=confusion["index"], columns=confusion["columns"])
    st.dataframe(cm_df, use_container_width=True)

st.subheader("Risk by plan tier")
risk_by_plan = (
    queue.groupby("plan_tier")["churn_probability"]
    .agg(["count", "mean"])
    .reset_index()
    .sort_values("mean", ascending=False)
)
st.plotly_chart(
    px.bar(
        risk_by_plan,
        x="plan_tier",
        y="mean",
        hover_data=["count"],
        title="Average churn probability among queued accounts",
    ),
    use_container_width=True,
)

st.subheader("Churn probability vs account value")
st.plotly_chart(
    px.scatter(
        queue.head(150),
        x="monthly_recurring_revenue",
        y="churn_probability",
        color="recommended_action",
        hover_data=["account_id", "risk_tier", "industry"],
        title="High-risk, high-value prioritization",
    ),
    use_container_width=True,
)

st.subheader("Feature relationships")
feature_x = st.selectbox(
    "X axis",
    ["days_since_last_activity", "feature_adoption_score", "support_tickets_90d", "payment_failures_90d"],
)
feature_y = st.selectbox(
    "Y axis",
    ["avg_weekly_sessions_30d", "transactions_30d", "nps_score", "monthly_recurring_revenue"],
)
st.plotly_chart(
    px.scatter(
        features.sample(min(len(features), 1000), random_state=42),
        x=feature_x,
        y=feature_y,
        color="churned_60d",
        title="Behavior and churn outcome view",
    ),
    use_container_width=True,
)
