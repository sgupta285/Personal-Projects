"""Visualization for product analytics."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from typing import Dict, List

plt.rcParams["figure.dpi"] = 150
sns.set_theme(style="whitegrid")


def plot_dau_wau_mau(metrics_df, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    ax1.plot(metrics_df["date"], metrics_df["dau"], label="DAU", color="#2196F3", linewidth=1)
    ax1.plot(metrics_df["date"], metrics_df["wau"], label="WAU", color="#4CAF50", linewidth=1)
    ax1.plot(metrics_df["date"], metrics_df["mau"], label="MAU", color="#FF9800", linewidth=1)
    ax1.set_ylabel("Active Users")
    ax1.set_title("User Engagement — DAU / WAU / MAU")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(metrics_df["date"], metrics_df["stickiness"] * 100, color="#9C27B0", linewidth=1)
    ax2.set_ylabel("Stickiness (DAU/MAU %)")
    ax2.set_xlabel("Date")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{output_dir}/dau_wau_mau.png", bbox_inches="tight")
    plt.close()


def plot_retention_heatmap(retention_table, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(14, 8))

    data = retention_table.iloc[:12, :12] * 100  # First 12 cohorts, 12 periods
    sns.heatmap(data, annot=True, fmt=".0f", cmap="YlOrRd_r", ax=ax,
                vmin=0, vmax=100, cbar_kws={"label": "Retention %"})
    ax.set_title("Cohort Retention Heatmap (%)")
    ax.set_xlabel("Period (weeks since signup)")
    ax.set_ylabel("Cohort")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/retention_heatmap.png", bbox_inches="tight")
    plt.close()


def plot_retention_curves(curves_by_segment, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 6))

    colors = plt.cm.Set2(np.linspace(0, 1, len(curves_by_segment)))
    for i, (seg, curve) in enumerate(curves_by_segment.items()):
        ax.plot(curve["day"], curve["retention_rate"] * 100, "o-",
                label=seg, color=colors[i], markersize=4)

    ax.set_xlabel("Days Since Signup")
    ax.set_ylabel("Retention Rate (%)")
    ax.set_title("Retention Curves by Segment")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/retention_curves.png", bbox_inches="tight")
    plt.close()


def plot_funnel(funnel_result, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    stages = funnel_result.stages
    labels = [s.stage for s in stages]
    values = [s.users for s in stages]
    rates = [s.rate_from_top * 100 for s in stages]

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.Blues(np.linspace(0.8, 0.3, len(stages)))
    bars = ax.barh(labels[::-1], values[::-1], color=colors)

    for bar, rate in zip(bars, rates[::-1]):
        ax.text(bar.get_width() + max(values) * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{rate:.1f}%", va="center", fontsize=10)

    ax.set_xlabel("Users")
    ax.set_title(f"Conversion Funnel (Overall: {funnel_result.overall_conversion*100:.1f}%)")
    ax.grid(True, alpha=0.3, axis="x")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/funnel.png", bbox_inches="tight")
    plt.close()


def plot_ab_test_results(results: List, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 5))

    metrics = [r.metric_name for r in results]
    lifts = [r.relative_lift_pct for r in results]
    ci_lo = [r.confidence_interval[0] * 100 / (r.control_mean if r.control_mean else 1) for r in results]
    ci_hi = [r.confidence_interval[1] * 100 / (r.control_mean if r.control_mean else 1) for r in results]
    sig = [r.is_significant for r in results]

    colors = ["#4CAF50" if s else "#9E9E9E" for s in sig]
    y_pos = range(len(metrics))

    ax.barh(y_pos, lifts, color=colors, alpha=0.7)
    for i in y_pos:
        ax.plot([ci_lo[i], ci_hi[i]], [i, i], color="black", linewidth=2)
    ax.axvline(0, color="red", linestyle="--", alpha=0.5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(metrics)
    ax.set_xlabel("Relative Lift (%)")
    ax.set_title("A/B Test Results (green = significant)")
    ax.grid(True, alpha=0.3, axis="x")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/ab_test_results.png", bbox_inches="tight")
    plt.close()


def plot_rfm_segments(rfm_segments, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    names = [s.segment_name for s in rfm_segments]
    sizes = [s.n_users for s in rfm_segments]
    monetary = [s.avg_monetary for s in rfm_segments]
    freq = [s.avg_frequency for s in rfm_segments]

    colors = plt.cm.Set2(np.linspace(0, 1, len(names)))

    axes[0].barh(names, sizes, color=colors)
    axes[0].set_title("Segment Size")
    axes[0].set_xlabel("Users")

    axes[1].barh(names, freq, color=colors)
    axes[1].set_title("Avg Frequency")
    axes[1].set_xlabel("Active Days")

    axes[2].barh(names, monetary, color=colors)
    axes[2].set_title("Avg Revenue")
    axes[2].set_xlabel("$")

    plt.suptitle("RFM Segmentation", fontsize=13)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/rfm_segments.png", bbox_inches="tight")
    plt.close()
