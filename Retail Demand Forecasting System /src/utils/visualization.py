"""
Visualization: forecast plots, feature importance, walk-forward results.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from typing import Dict, List

plt.rcParams["figure.dpi"] = 150
sns.set_theme(style="whitegrid")


def plot_forecast_vs_actual(
    dates, actual, predicted, model_name="Model", output_dir="output"
):
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(dates, actual, label="Actual", color="#2196F3", linewidth=1, alpha=0.8)
    ax.plot(dates, predicted, label=f"{model_name} Forecast", color="#F44336",
            linewidth=1, linestyle="--", alpha=0.8)
    ax.fill_between(dates, actual, predicted, alpha=0.1, color="gray")
    ax.set_title(f"Demand Forecast — {model_name}", fontsize=13)
    ax.set_xlabel("Date")
    ax.set_ylabel("Quantity")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/forecast_{model_name.lower()}.png", bbox_inches="tight")
    plt.close()


def plot_feature_importance(importance: pd.Series, model_name="XGBoost", output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 8))
    importance.sort_values().plot.barh(ax=ax, color="#4CAF50", alpha=0.8)
    ax.set_title(f"Feature Importance — {model_name}", fontsize=13)
    ax.set_xlabel("Importance Score")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/feature_importance_{model_name.lower()}.png", bbox_inches="tight")
    plt.close()


def plot_walk_forward_mape(
    model_results: Dict[str, List], output_dir="output"
):
    """Plot MAPE across walk-forward windows for each model."""
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(14, 5))

    colors = {"xgboost": "#2196F3", "lightgbm": "#4CAF50",
              "prophet": "#FF9800", "sarima": "#9C27B0", "ensemble": "#F44336"}

    for model_name, results in model_results.items():
        mapes = [r.metrics.mape for r in results]
        ax.plot(range(len(mapes)), mapes, "o-", label=model_name,
                color=colors.get(model_name, "gray"), markersize=4)

    ax.set_title("Walk-Forward MAPE by Window", fontsize=13)
    ax.set_xlabel("Window #")
    ax.set_ylabel("MAPE (%)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/wf_mape.png", bbox_inches="tight")
    plt.close()


def plot_residuals(actual, predicted, model_name="Model", output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    residuals = np.array(actual) - np.array(predicted)

    fig, axes = plt.subplots(1, 3, figsize=(16, 4))

    # Histogram
    axes[0].hist(residuals, bins=50, color="#2196F3", alpha=0.7, edgecolor="white")
    axes[0].axvline(0, color="red", linestyle="--")
    axes[0].set_title("Residual Distribution")
    axes[0].set_xlabel("Residual")

    # QQ-like scatter
    axes[1].scatter(predicted, residuals, alpha=0.3, s=8, color="#4CAF50")
    axes[1].axhline(0, color="red", linestyle="--")
    axes[1].set_title("Residuals vs Predicted")
    axes[1].set_xlabel("Predicted")
    axes[1].set_ylabel("Residual")

    # Actual vs Predicted
    axes[2].scatter(actual, predicted, alpha=0.3, s=8, color="#FF9800")
    lims = [min(min(actual), min(predicted)), max(max(actual), max(predicted))]
    axes[2].plot(lims, lims, "r--", alpha=0.5)
    axes[2].set_title("Actual vs Predicted")
    axes[2].set_xlabel("Actual")
    axes[2].set_ylabel("Predicted")

    plt.suptitle(f"Residual Analysis — {model_name}", fontsize=13)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/residuals_{model_name.lower()}.png", bbox_inches="tight")
    plt.close()


def plot_demand_decomposition(df: pd.DataFrame, output_dir="output"):
    """Plot demand decomposition: trend, weekly, monthly patterns."""
    os.makedirs(output_dir, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Daily demand over time
    daily = df.groupby("date")["quantity"].sum()
    axes[0, 0].plot(daily.index, daily.values, linewidth=0.5, color="#2196F3")
    axes[0, 0].plot(daily.index, daily.rolling(28).mean(), color="red", linewidth=1.5, label="28d MA")
    axes[0, 0].set_title("Daily Total Demand")
    axes[0, 0].legend()

    # Day of week pattern
    dow = df.groupby("day_of_week")["quantity"].mean()
    axes[0, 1].bar(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                   dow.values, color="#4CAF50", alpha=0.8)
    axes[0, 1].set_title("Avg Demand by Day of Week")

    # Monthly pattern
    monthly = df.groupby("month")["quantity"].mean()
    axes[1, 0].bar(range(1, 13), monthly.values, color="#FF9800", alpha=0.8)
    axes[1, 0].set_title("Avg Demand by Month")
    axes[1, 0].set_xlabel("Month")

    # Promotion effect
    if "is_promotion" in df.columns:
        promo_groups = df.groupby("is_promotion")["quantity"].mean()
        axes[1, 1].bar(["No Promo", "Promo"], promo_groups.values,
                       color=["#9E9E9E", "#F44336"], alpha=0.8)
        axes[1, 1].set_title("Promotion Effect on Demand")

    plt.suptitle("Demand Decomposition", fontsize=14)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/demand_decomposition.png", bbox_inches="tight")
    plt.close()
