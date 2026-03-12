from __future__ import annotations

import json
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

from ecomopt.ab_testing import compare_variants, segment_lift_table, summarize_experiment
from ecomopt.config import settings


def build_reports(outputs: dict[str, pd.DataFrame], artifact_dir: Path) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = artifact_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    stage_metrics = outputs["funnel_stage_metrics"]
    cohorts = outputs["experiment_cohorts"]
    segment_metrics = outputs["funnel_segment_metrics"]

    experiment_summary = compare_variants(cohorts)
    segment_lift = segment_lift_table(cohorts, ["device_type", "traffic_channel", "user_recency", "product_category"])
    session_metrics = summarize_experiment(cohorts)
    funnel_summary = {
        "top_leak_stage": stage_metrics.sort_values("dropoff_from_previous", ascending=False).iloc[0]["stage_name"],
        "landing_sessions": int(stage_metrics.loc[stage_metrics["stage_name"] == "landing", "sessions_at_stage"].iloc[0]),
        "purchase_sessions": int(stage_metrics.loc[stage_metrics["stage_name"] == "purchase", "sessions_at_stage"].iloc[0]),
        "overall_purchase_rate": round(float(stage_metrics.loc[stage_metrics["stage_name"] == "purchase", "sessions_at_stage"].iloc[0]) / float(stage_metrics.loc[stage_metrics["stage_name"] == "landing", "sessions_at_stage"].iloc[0]), 6),
    }

    (artifact_dir / "experiment_summary.json").write_text(json.dumps(experiment_summary, indent=2))
    (artifact_dir / "funnel_summary.json").write_text(json.dumps(funnel_summary, indent=2))
    segment_lift.to_csv(artifact_dir / "segment_lift_summary.csv", index=False)
    session_metrics.to_csv(artifact_dir / "session_metrics.csv", index=False)

    _write_memo(artifact_dir, experiment_summary, segment_lift)
    _plot_funnel(stage_metrics, fig_dir)
    _plot_variant_conversion(session_metrics, fig_dir)
    _plot_mobile_channel_lift(segment_metrics, fig_dir)


def _write_memo(artifact_dir: Path, summary: dict, segment_lift: pd.DataFrame) -> None:
    strongest = segment_lift.head(5).copy()
    strongest["segment"] = strongest[["device_type", "traffic_channel", "user_recency", "product_category"]].agg(" | ".join, axis=1)
    lines = [
        "# Experiment Summary",
        "",
        f"- Control conversion rate: {summary['control_conversion_rate']:.2%}",
        f"- Treatment conversion rate: {summary['treatment_conversion_rate']:.2%}",
        f"- Absolute lift: {summary['absolute_lift']:.2%}",
        f"- Relative lift: {summary['relative_lift']:.2%}",
        f"- p-value: {summary['p_value']:.4f}",
        f"- Observed power: {summary['observed_power']:.2%}",
        f"- MDE at 80% power: {summary['mde_at_80_power']:.2%}",
        "",
        "## Strongest treatment segments",
        "",
    ]
    for row in strongest.itertuples(index=False):
        lines.append(f"- {row.segment}: {row.absolute_lift:.2%} absolute lift")
    lines.extend([
        "",
        "## Recommendation",
        "",
        "Roll the treatment out first to the strongest high-friction segments and keep learning before a universal launch.",
    ])
    (artifact_dir / "recommendation_memo.md").write_text("\n".join(lines))


def _plot_funnel(stage_metrics: pd.DataFrame, fig_dir: Path) -> None:
    plt.figure(figsize=(9, 5))
    plt.bar(stage_metrics["stage_name"], stage_metrics["sessions_at_stage"])
    plt.title("Sessions by funnel stage")
    plt.ylabel("Sessions")
    plt.tight_layout()
    plt.savefig(fig_dir / "funnel_stage_counts.png", dpi=160)
    plt.close()


def _plot_variant_conversion(session_metrics: pd.DataFrame, fig_dir: Path) -> None:
    plt.figure(figsize=(7, 4.5))
    plt.bar(session_metrics["variant"], session_metrics["conversion_rate"])
    plt.title("Purchase conversion by variant")
    plt.ylabel("Conversion rate")
    plt.tight_layout()
    plt.savefig(fig_dir / "variant_conversion.png", dpi=160)
    plt.close()


def _plot_mobile_channel_lift(segment_metrics: pd.DataFrame, fig_dir: Path) -> None:
    mobile = segment_metrics[segment_metrics["device_type"] == "mobile"].copy()
    pivot = mobile.pivot_table(index="traffic_channel", columns="variant", values="purchase_rate", aggfunc="mean", fill_value=0)
    if {"control", "treatment"}.issubset(pivot.columns):
        pivot["lift"] = pivot["treatment"] - pivot["control"]
        pivot = pivot.sort_values("lift", ascending=False)
        plt.figure(figsize=(9, 5))
        plt.bar(pivot.index, pivot["lift"])
        plt.title("Mobile purchase lift by channel")
        plt.ylabel("Absolute lift")
        plt.xticks(rotation=20)
        plt.tight_layout()
        plt.savefig(fig_dir / "mobile_channel_lift.png", dpi=160)
        plt.close()
