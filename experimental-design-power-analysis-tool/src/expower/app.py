from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from expower.analysis_plan import recommend_analysis_plan
from expower.power import (
    ClusteredDesignInputs,
    PairedDesignInputs,
    TwoSampleDesignInputs,
    cost_curve,
    recommend_clustered_design,
    recommend_paired_design,
    recommend_two_sample_design,
)

st.set_page_config(page_title="Experimental Design and Power Analysis Tool", layout="wide")
st.title("Experimental Design and Power Analysis Tool")
st.caption("A practical planning tool for A/B tests, repeated-measures experiments, and clustered rollouts.")

with st.sidebar:
    design = st.selectbox(
        "Design type",
        ["between_subjects", "within_subjects", "clustered"],
    )
    alpha = st.slider("Alpha", 0.01, 0.10, 0.05, step=0.01)
    power = st.slider("Target power", 0.60, 0.99, 0.80, step=0.01)
    effect_size = st.slider("Standardized effect size", 0.05, 1.00, 0.30, step=0.01)
    budget = st.number_input("Budget", min_value=0.0, value=2500.0, step=100.0)
    treatment_cost = st.number_input("Treatment cost per unit", min_value=0.5, value=1.2, step=0.1)
    control_cost = st.number_input("Control cost per unit", min_value=0.5, value=1.0, step=0.1)

if design == "between_subjects":
    outcome_type = st.radio("Outcome type", ["continuous", "binary"], horizontal=True)
    inputs = TwoSampleDesignInputs(
        outcome_type=outcome_type,
        alpha=alpha,
        power=power,
        effect_size=effect_size,
        treatment_cost=treatment_cost,
        control_cost=control_cost,
        budget=budget or None,
        baseline_rate=0.2,
        alternative_rate=min(0.95, 0.2 + effect_size * 0.05),
    )
    rec = recommend_two_sample_design(inputs)
elif design == "within_subjects":
    rec = recommend_paired_design(
        PairedDesignInputs(
            alpha=alpha,
            power=power,
            effect_size=effect_size,
            cost_per_subject=max(treatment_cost, control_cost),
            budget=budget or None,
        )
    )
    outcome_type = "continuous"
else:
    icc = st.slider("Intraclass correlation (ICC)", 0.0, 0.30, 0.05, step=0.01)
    avg_cluster_size = st.slider("Average cluster size", 4, 100, 20, step=1)
    rec = recommend_clustered_design(
        ClusteredDesignInputs(
            alpha=alpha,
            power=power,
            effect_size=effect_size,
            icc=icc,
            avg_cluster_size=avg_cluster_size,
            treatment_cost=treatment_cost,
            control_cost=control_cost,
            budget=budget or None,
        )
    )
    outcome_type = "continuous"

plan = recommend_analysis_plan(
    design_type=rec.design_type,
    outcome_type=outcome_type,
    covariates_available=True,
    clustering_present=rec.design_type == "clustered",
)

left, right = st.columns(2)
with left:
    st.subheader("Design recommendation")
    st.json(rec.to_dict())
with right:
    st.subheader("Analysis plan")
    st.json(plan.to_dict())

curve = pd.DataFrame(
    cost_curve(
        max_budget=int(max(500, budget or 2500)),
        design="paired" if rec.design_type == "within_subjects" else ("clustered" if rec.design_type == "clustered" else "between"),
        effect_size=effect_size,
        alpha=alpha,
        power=power,
    )
)

st.subheader("Budget sensitivity")
fig = px.line(curve, x="budget", y="mde", markers=True, title="Minimum detectable effect vs budget")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Planning notes")
for note in rec.notes:
    st.write(f"- {note}")
