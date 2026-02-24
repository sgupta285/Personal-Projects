"""Visualization for minimum wage employment effects analysis."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from typing import List, Dict

plt.rcParams["figure.dpi"] = 150
sns.set_theme(style="whitegrid")


def plot_parallel_trends(df, treatment_quarter, outcome="employment_rate", output_dir="output"):
    """Plot treated vs control group trends over time."""
    os.makedirs(output_dir, exist_ok=True)

    treated = df[df["treated"] == 1].groupby("quarter")[outcome].mean()
    control = df[df["treated"] == 0].groupby("quarter")[outcome].mean()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(treated.index, treated.values, "o-", label="Treated States", color="#F44336", markersize=3)
    ax.plot(control.index, control.values, "o-", label="Control States", color="#2196F3", markersize=3)
    ax.axvline(treatment_quarter, color="black", linestyle="--", alpha=0.6, label="Policy Change")
    ax.fill_betweenx(ax.get_ylim(), treatment_quarter, df["quarter"].max(),
                     alpha=0.05, color="gray")
    ax.set_xlabel("Quarter")
    ax.set_ylabel(outcome.replace("_", " ").title())
    ax.set_title("Parallel Trends: Treated vs Control")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/parallel_trends.png", bbox_inches="tight")
    plt.close()


def plot_event_study(event_result, output_dir="output"):
    """Plot event study coefficients with confidence intervals."""
    os.makedirs(output_dir, exist_ok=True)
    coefs = event_result.coefficients

    periods = [c.relative_period for c in coefs]
    estimates = [c.estimate for c in coefs]
    ci_lo = [c.ci_lower for c in coefs]
    ci_hi = [c.ci_upper for c in coefs]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.errorbar(periods, estimates, yerr=[np.array(estimates) - np.array(ci_lo),
                np.array(ci_hi) - np.array(estimates)],
                fmt="o", capsize=3, color="#2196F3", markersize=5, linewidth=1)
    ax.axhline(0, color="red", linestyle="--", alpha=0.5)
    ax.axvline(-0.5, color="black", linestyle="--", alpha=0.4, label="Treatment")
    ax.fill_between(range(0, max(periods) + 1), ax.get_ylim()[0], ax.get_ylim()[1],
                    alpha=0.03, color="orange")
    ax.set_xlabel("Quarters Relative to Treatment")
    ax.set_ylabel("Treatment Effect Estimate")
    ax.set_title(f"Event Study — {event_result.outcome}\n"
                 f"(Pre-trend p={event_result.pre_trend_p_value:.3f}, "
                 f"{'✓' if event_result.parallel_trends_hold else '✗'} parallel trends)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/event_study.png", bbox_inches="tight")
    plt.close()


def plot_synthetic_control(sc_result, treatment_quarter, output_dir="output"):
    """Plot treated vs synthetic control series."""
    os.makedirs(output_dir, exist_ok=True)
    n = len(sc_result.treated_series)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    quarters = range(n)
    ax1.plot(quarters, sc_result.treated_series, "o-", label=f"Treated: {sc_result.treated_state}",
             color="#F44336", markersize=3)
    ax1.plot(quarters, sc_result.synthetic_series, "o-", label="Synthetic Control",
             color="#2196F3", markersize=3)
    ax1.axvline(treatment_quarter, color="black", linestyle="--", alpha=0.6)
    ax1.set_ylabel("Employment Rate")
    ax1.set_title(f"Synthetic Control — {sc_result.treated_state}\n"
                  f"(Pre-RMSPE: {sc_result.pre_rmspe:.4f})")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Gap plot
    gap = np.array(sc_result.treated_series) - np.array(sc_result.synthetic_series)
    ax2.plot(quarters, gap, "o-", color="#4CAF50", markersize=3)
    ax2.axhline(0, color="red", linestyle="--", alpha=0.5)
    ax2.axvline(treatment_quarter, color="black", linestyle="--", alpha=0.6)
    ax2.fill_between(range(treatment_quarter, n), 0, gap[treatment_quarter:],
                     alpha=0.15, color="green" if np.mean(gap[treatment_quarter:]) < 0 else "red")
    ax2.set_xlabel("Quarter")
    ax2.set_ylabel("Gap (Treated - Synthetic)")
    ax2.set_title(f"Treatment Effect: {sc_result.estimated_effect:.4f}")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{output_dir}/synthetic_control.png", bbox_inches="tight")
    plt.close()


def plot_rdd(df, rdd_result, cutoff=10.0, output_dir="output"):
    """Plot RDD with fitted lines on each side of cutoff."""
    os.makedirs(output_dir, exist_ok=True)
    bw = rdd_result.bandwidth
    data = df[(df["min_wage"] >= cutoff - bw) & (df["min_wage"] <= cutoff + bw)]

    fig, ax = plt.subplots(figsize=(10, 6))
    below = data[data["min_wage"] < cutoff]
    above = data[data["min_wage"] >= cutoff]

    ax.scatter(below["min_wage"], below["employment_rate"], alpha=0.15, s=8, color="#2196F3", label="Below cutoff")
    ax.scatter(above["min_wage"], above["employment_rate"], alpha=0.15, s=8, color="#F44336", label="Above cutoff")
    ax.axvline(cutoff, color="black", linestyle="--", alpha=0.6, label=f"Cutoff: ${cutoff:.2f}")

    # Fit lines
    for side, color in [(below, "#2196F3"), (above, "#F44336")]:
        if len(side) > 10:
            z = np.polyfit(side["min_wage"], side["employment_rate"], 1)
            x_line = np.linspace(side["min_wage"].min(), side["min_wage"].max(), 50)
            ax.plot(x_line, np.polyval(z, x_line), color=color, linewidth=2)

    ax.set_xlabel("Minimum Wage ($/hr)")
    ax.set_ylabel("Employment Rate")
    ax.set_title(f"RDD: τ̂ = {rdd_result.estimate:.4f} (p={rdd_result.p_value:.3f})")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/rdd.png", bbox_inches="tight")
    plt.close()


def plot_robustness_summary(checks, output_dir="output"):
    """Plot robustness check results."""
    os.makedirs(output_dir, exist_ok=True)
    names = [c.test_name for c in checks]
    passes = [c.passes for c in checks]
    colors = ["#4CAF50" if p else "#F44336" for p in passes]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.barh(names, [1] * len(names), color=colors, alpha=0.7)
    for i, c in enumerate(checks):
        label = "PASS" if c.passes else "FAIL"
        ax.text(0.5, i, f"{label}: {c.notes}", va="center", fontsize=9)

    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.set_title("Robustness Checks Summary")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/robustness.png", bbox_inches="tight")
    plt.close()
