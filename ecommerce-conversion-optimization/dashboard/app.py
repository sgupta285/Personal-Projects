from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
PROCESSED_DIR = ROOT / "data/processed"

st.set_page_config(page_title="Conversion Optimization Dashboard", layout="wide")
st.title("E-Commerce Conversion Optimization")

required = [
    ARTIFACT_DIR / "experiment_summary.json",
    ARTIFACT_DIR / "segment_lift_summary.csv",
    PROCESSED_DIR / "funnel_stage_metrics.csv",
    PROCESSED_DIR / "experiment_cohorts.csv",
]
if not all(path.exists() for path in required):
    st.warning("Run `make bootstrap` first.")
    st.stop()

summary = json.loads((ARTIFACT_DIR / "experiment_summary.json").read_text())
stage_metrics = pd.read_csv(PROCESSED_DIR / "funnel_stage_metrics.csv")
cohorts = pd.read_csv(PROCESSED_DIR / "experiment_cohorts.csv")
segment_lift = pd.read_csv(ARTIFACT_DIR / "segment_lift_summary.csv")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Control CVR", f"{summary['control_conversion_rate']:.2%}")
c2.metric("Treatment CVR", f"{summary['treatment_conversion_rate']:.2%}")
c3.metric("Absolute lift", f"{summary['absolute_lift']:.2%}")
c4.metric("p-value", f"{summary['p_value']:.4f}")

st.subheader("Funnel leakage")
st.dataframe(stage_metrics, use_container_width=True)
st.plotly_chart(px.bar(stage_metrics, x="stage_name", y="sessions_at_stage", title="Sessions by stage"), use_container_width=True)

st.subheader("Top treatment segments")
st.dataframe(segment_lift.head(20), use_container_width=True)

segment = st.selectbox("Segment dimension", ["device_type", "traffic_channel", "product_category", "user_recency"])
plot_df = cohorts.groupby([segment, "variant"])["purchased"].mean().reset_index()
st.plotly_chart(px.bar(plot_df, x=segment, y="purchased", color="variant", barmode="group", title=f"Purchase rate by {segment}"), use_container_width=True)
