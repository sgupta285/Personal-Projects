from __future__ import annotations

import json

import matplotlib.pyplot as plt
import pandas as pd

from churnintel.config import settings


def generate_preview_images() -> None:
    settings.screenshots_dir.mkdir(parents=True, exist_ok=True)

    feature_path = settings.feature_data_path
    metrics_path = settings.artifact_dir / "metrics.json"
    queue_path = settings.artifact_dir / "top_risk_accounts.csv"

    if not (feature_path.exists() and metrics_path.exists() and queue_path.exists()):
        return

    features = pd.read_csv(feature_path)
    queue = pd.read_csv(queue_path)
    metrics = json.loads(metrics_path.read_text())

    fig = plt.figure(figsize=(10, 6))
    plt.scatter(
        queue["monthly_recurring_revenue"].head(120),
        queue["churn_probability"].head(120),
        alpha=0.65,
    )
    plt.xlabel("Monthly recurring revenue")
    plt.ylabel("Churn probability")
    plt.title("Top risk accounts by value")
    plt.tight_layout()
    fig.savefig(settings.screenshots_dir / "top-risk-accounts.png", dpi=150)
    plt.close(fig)

    fig = plt.figure(figsize=(10, 6))
    churned = features[features["churned_60d"] == 1]["days_since_last_activity"]
    retained = features[features["churned_60d"] == 0]["days_since_last_activity"]
    plt.hist(retained, bins=25, alpha=0.7, label="retained")
    plt.hist(churned, bins=25, alpha=0.7, label="churned")
    plt.xlabel("Days since last activity")
    plt.ylabel("Accounts")
    plt.title("Recency distribution by churn label")
    plt.legend()
    plt.tight_layout()
    fig.savefig(settings.screenshots_dir / "recency-distribution.png", dpi=150)
    plt.close(fig)

    fig = plt.figure(figsize=(10, 4))
    metric_names = ["roc_auc", "pr_auc", "precision_at_10_pct", "recall_at_10_pct"]
    metric_values = [metrics[name] for name in metric_names]
    plt.bar(metric_names, metric_values)
    plt.ylim(0, 1.0)
    plt.ylabel("Score")
    plt.title("Model performance summary")
    plt.tight_layout()
    fig.savefig(settings.screenshots_dir / "model-metrics.png", dpi=150)
    plt.close(fig)
