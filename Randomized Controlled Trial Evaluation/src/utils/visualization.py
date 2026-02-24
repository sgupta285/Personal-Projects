"""Visualization for RCT Evaluation."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from typing import List, Dict

plt.rcParams["figure.dpi"] = 150
sns.set_theme(style="whitegrid")


def plot_balance(balance_table, output_dir="output"):
    """Love plot: SMD for each covariate."""
    os.makedirs(output_dir, exist_ok=True)
    rows = balance_table.rows

    fig, ax = plt.subplots(figsize=(8, max(4, len(rows) * 0.5)))
    names = [r.covariate for r in rows]
    smds = [r.smd for r in rows]
    colors = ["#4CAF50" if r.balanced else "#F44336" for r in rows]

    ax.barh(names, smds, color=colors, alpha=0.7)
    ax.axvline(-0.10, color="red", linestyle="--", alpha=0.4)
    ax.axvline(0.10, color="red", linestyle="--", alpha=0.4, label="±0.10 threshold")
    ax.axvline(0, color="black", linewidth=0.5)
    ax.set_xlabel("Standardized Mean Difference")
    ax.set_title(f"Covariate Balance (Love Plot) — {balance_table.n_imbalanced} imbalanced")
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/balance_love_plot.png", bbox_inches="tight")
    plt.close()


def plot_ate_comparison(results, output_dir="output"):
    """Forest plot: compare ATE estimates across methods."""
    os.makedirs(output_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, max(4, len(results) * 0.6)))
    methods = [r.method for r in results]
    estimates = [r.estimate for r in results]
    ci_lo = [r.ci_lower for r in results]
    ci_hi = [r.ci_upper for r in results]

    y_pos = range(len(methods))
    colors = ["#2196F3"] * len(methods)

    ax.errorbar(estimates, y_pos,
                xerr=[[e - lo for e, lo in zip(estimates, ci_lo)],
                      [hi - e for e, hi in zip(estimates, ci_hi)]],
                fmt="o", capsize=4, color="#2196F3", markersize=8, linewidth=2)

    # True value
    true_vals = [r.true_value for r in results if r.true_value is not None]
    if true_vals:
        ax.axvline(true_vals[0], color="red", linestyle="--", alpha=0.6, label=f"True: {true_vals[0]}")
    ax.axvline(0, color="gray", linestyle="-", alpha=0.3)

    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(methods)
    ax.set_xlabel("Treatment Effect Estimate")
    ax.set_title("ATE / LATE Estimates Across Methods (95% CI)")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="x")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/ate_forest_plot.png", bbox_inches="tight")
    plt.close()


def plot_cate_subgroups(cate_results, subgroup_name, output_dir="output"):
    """Bar chart of CATE by subgroup with CIs and true values."""
    os.makedirs(output_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    labels = [r.subgroup_value for r in cate_results]
    estimates = [r.estimate for r in cate_results]
    ci_lo = [r.ci_lower for r in cate_results]
    ci_hi = [r.ci_upper for r in cate_results]
    true_vals = [r.true_cate for r in cate_results]

    x = np.arange(len(labels))
    width = 0.35

    bars = ax.bar(x - width / 2, estimates, width, label="Estimated CATE", color="#2196F3", alpha=0.7)
    ax.errorbar(x - width / 2, estimates,
                yerr=[[e - lo for e, lo in zip(estimates, ci_lo)],
                      [hi - e for e, hi in zip(estimates, ci_hi)]],
                fmt="none", capsize=4, color="black")

    if any(v is not None for v in true_vals):
        true_plot = [v if v is not None else 0 for v in true_vals]
        ax.bar(x + width / 2, true_plot, width, label="True CATE", color="#F44336", alpha=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Treatment Effect")
    ax.set_title(f"Heterogeneous Treatment Effects by {subgroup_name}")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/cate_{subgroup_name}.png", bbox_inches="tight")
    plt.close()


def plot_gates(gates_result, output_dir="output"):
    """GATES: group average treatment effects by predicted CATE quintile."""
    os.makedirs(output_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    n_groups = len(gates_result.group_estimates)
    x = range(1, n_groups + 1)
    est = gates_result.group_estimates
    ses = gates_result.group_ses

    ax.bar(x, est, color=plt.cm.RdYlGn(np.linspace(0.2, 0.8, n_groups)), alpha=0.7,
           yerr=[1.96 * s for s in ses], capsize=4)
    ax.axhline(np.mean(est), color="red", linestyle="--", alpha=0.5, label="Overall ATE")
    ax.set_xlabel("CATE Quintile (1=lowest, 5=highest)")
    ax.set_ylabel("Group Average Treatment Effect")
    ax.set_title(f"GATES Analysis (Heterogeneity p={gates_result.heterogeneity_p:.4f})")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/gates.png", bbox_inches="tight")
    plt.close()


def plot_cate_distribution(cate_predictions, true_te=None, output_dir="output"):
    """Distribution of individual CATE predictions."""
    os.makedirs(output_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(cate_predictions, bins=50, color="#2196F3", alpha=0.6, density=True, label="Predicted τ̂(x)")
    if true_te is not None:
        ax.hist(true_te, bins=50, color="#F44336", alpha=0.4, density=True, label="True τ(x)")
    ax.axvline(np.mean(cate_predictions), color="blue", linestyle="--", label=f"Mean τ̂={np.mean(cate_predictions):.2f}")
    ax.set_xlabel("Individual Treatment Effect")
    ax.set_ylabel("Density")
    ax.set_title("Distribution of Heterogeneous Treatment Effects")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/cate_distribution.png", bbox_inches="tight")
    plt.close()


def plot_bootstrap(boot_dist, observed, ci, output_dir="output"):
    """Bootstrap distribution with observed ATE and CI."""
    os.makedirs(output_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(boot_dist, bins=60, color="#9C27B0", alpha=0.5, density=True)
    ax.axvline(observed, color="red", linewidth=2, label=f"Observed: {observed:.3f}")
    ax.axvline(ci[0], color="orange", linestyle="--", label=f"95% CI: [{ci[0]:.3f}, {ci[1]:.3f}]")
    ax.axvline(ci[1], color="orange", linestyle="--")
    ax.set_xlabel("ATE Estimate")
    ax.set_ylabel("Density")
    ax.set_title("Bootstrap Distribution of ATE")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/bootstrap.png", bbox_inches="tight")
    plt.close()
