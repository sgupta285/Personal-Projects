"""
Visualization for demand elasticity analysis.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from typing import List, Dict

plt.rcParams["figure.dpi"] = 150
sns.set_theme(style="whitegrid")


def plot_demand_curves(products, elasticities: Dict[str, float], output_dir="output"):
    """Plot demand curves for each product showing price sensitivity."""
    os.makedirs(output_dir, exist_ok=True)
    n = min(len(products), 8)
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()

    colors = plt.cm.Set2(np.linspace(0, 1, n))
    for i, prod in enumerate(products[:n]):
        ax = axes[i]
        e = elasticities.get(prod.product_id, prod.own_elasticity)
        p = np.linspace(prod.base_price * 0.5, prod.base_price * 2.0, 100)
        q = prod.base_quantity * (p / prod.base_price) ** e

        ax.plot(p, q, color=colors[i], linewidth=2)
        ax.axvline(prod.base_price, color="gray", linestyle="--", alpha=0.4)
        ax.scatter([prod.base_price], [prod.base_quantity], color="red", zorder=5, s=40)
        ax.set_title(f"{prod.product_id} ({prod.category})\nε = {e:.2f}", fontsize=10)
        ax.set_xlabel("Price ($)")
        ax.set_ylabel("Quantity")
        ax.grid(True, alpha=0.3)

    for j in range(n, len(axes)):
        axes[j].set_visible(False)

    plt.suptitle("Demand Curves by Product", fontsize=14)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/demand_curves.png", bbox_inches="tight")
    plt.close()


def plot_cross_elasticity_heatmap(matrix, product_ids, output_dir="output"):
    """Plot cross-price elasticity heatmap."""
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 8))

    mask = np.abs(matrix) < 0.01  # Mask near-zero values
    sns.heatmap(
        matrix, annot=True, fmt=".2f", cmap="RdBu_r", center=0,
        xticklabels=product_ids, yticklabels=product_ids,
        mask=mask, ax=ax, vmin=-2.5, vmax=0.5,
        cbar_kws={"label": "Elasticity"},
    )
    ax.set_title("Cross-Price Elasticity Matrix\n(diagonal = own-price, off-diagonal = cross-price)",
                 fontsize=13)
    ax.set_xlabel("Price of Product j")
    ax.set_ylabel("Quantity of Product i")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/cross_elasticity_heatmap.png", bbox_inches="tight")
    plt.close()


def plot_revenue_optimization(products, elasticities, output_dir="output"):
    """Plot revenue and profit curves with optimal price marked."""
    os.makedirs(output_dir, exist_ok=True)
    n = min(len(products), 4)
    fig, axes = plt.subplots(1, n, figsize=(4 * n, 5))
    if n == 1:
        axes = [axes]

    for i, prod in enumerate(products[:n]):
        ax = axes[i]
        e = elasticities.get(prod.product_id, prod.own_elasticity)
        mc = prod.marginal_cost
        p = np.linspace(mc * 1.05, prod.base_price * 2.5, 100)
        q = prod.base_quantity * (p / prod.base_price) ** e
        revenue = p * q
        profit = (p - mc) * q

        ax.plot(p, revenue, color="#2196F3", label="Revenue", linewidth=1.5)
        ax.plot(p, profit, color="#4CAF50", label="Profit", linewidth=1.5)
        ax.axvline(prod.base_price, color="gray", linestyle="--", alpha=0.4, label="Current")

        # Mark optimal
        opt_idx = np.argmax(profit)
        ax.axvline(p[opt_idx], color="red", linestyle=":", alpha=0.6, label=f"Optimal ${p[opt_idx]:.2f}")
        ax.scatter([p[opt_idx]], [profit[opt_idx]], color="red", zorder=5, s=50)

        ax.set_title(f"{prod.product_id} (ε={e:.2f})", fontsize=10)
        ax.set_xlabel("Price ($)")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.suptitle("Revenue & Profit Optimization", fontsize=13)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/revenue_optimization.png", bbox_inches="tight")
    plt.close()


def plot_elasticity_comparison(results_by_method: Dict[str, List], output_dir="output"):
    """Compare elasticity estimates across OLS, Panel FE, and IV methods."""
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 6))

    methods = list(results_by_method.keys())
    product_ids = [r.product_id for r in results_by_method[methods[0]]]
    x = np.arange(len(product_ids))
    width = 0.22

    colors = {"OLS Log-Log": "#2196F3", "Panel FE (Clustered SE)": "#4CAF50",
              "IV/2SLS": "#FF9800", "True": "#F44336"}

    for i, method in enumerate(methods):
        vals = [r.own_elasticity for r in results_by_method[method]]
        errs = [1.96 * r.std_error for r in results_by_method[method]]
        ax.bar(x + i * width, vals, width, label=method,
               color=colors.get(method, "gray"), alpha=0.8, yerr=errs, capsize=3)

    # True values
    if results_by_method[methods[0]][0].true_elasticity is not None:
        true_vals = [r.true_elasticity for r in results_by_method[methods[0]]]
        ax.scatter(x + width * len(methods) / 2, true_vals,
                   color="red", marker="*", s=100, zorder=5, label="True ε")

    ax.set_xlabel("Product")
    ax.set_ylabel("Own-Price Elasticity")
    ax.set_title("Elasticity Estimates by Method (with 95% CI)", fontsize=13)
    ax.set_xticks(x + width * len(methods) / 2)
    ax.set_xticklabels(product_ids)
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/elasticity_comparison.png", bbox_inches="tight")
    plt.close()


def plot_price_quantity_scatter(df, product_id, output_dir="output"):
    """Scatter plot of log(price) vs log(quantity) for a product."""
    os.makedirs(output_dir, exist_ok=True)
    prod_data = df[df["product_id"] == product_id]

    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(
        prod_data["log_price"], prod_data["log_quantity"],
        c=prod_data["is_promotion"].astype(int), cmap="RdYlGn_r",
        alpha=0.5, s=15, edgecolors="none",
    )
    # Add OLS fit line
    z = np.polyfit(prod_data["log_price"], prod_data["log_quantity"], 1)
    p_line = np.linspace(prod_data["log_price"].min(), prod_data["log_price"].max(), 100)
    ax.plot(p_line, np.polyval(z, p_line), color="red", linewidth=2,
            label=f"ε̂ = {z[0]:.2f}")

    ax.set_xlabel("ln(Price)")
    ax.set_ylabel("ln(Quantity)")
    ax.set_title(f"Price-Quantity Relationship — {product_id}", fontsize=13)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.colorbar(scatter, label="On Promotion")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/scatter_{product_id}.png", bbox_inches="tight")
    plt.close()
