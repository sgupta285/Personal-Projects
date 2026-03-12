from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import shap
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from churnintel.features import TARGET_COLUMN, model_input_frame
from churnintel.interventions import choose_intervention, risk_tier


def precision_at_k(y_true: pd.Series, y_score: np.ndarray, fraction: float = 0.10) -> float:
    k = max(1, int(len(y_true) * fraction))
    ranking = np.argsort(y_score)[::-1][:k]
    return float(np.mean(np.asarray(y_true)[ranking]))


def recall_at_k(y_true: pd.Series, y_score: np.ndarray, fraction: float = 0.10) -> float:
    positives = max(1, int(np.sum(y_true)))
    k = max(1, int(len(y_true) * fraction))
    ranking = np.argsort(y_score)[::-1][:k]
    return float(np.sum(np.asarray(y_true)[ranking]) / positives)


def simulated_retention_uplift(queue_df: pd.DataFrame) -> float:
    save_rates = {
        "Direct CSM outreach with recovery plan": 0.28,
        "Targeted save offer and executive check-in": 0.18,
        "Billing recovery sequence plus product education": 0.16,
        "Customer success outreach plus onboarding refresh": 0.15,
        "Lifecycle email with tailored value proof": 0.09,
        "Education campaign and in-app guidance": 0.05,
        "Monitor only": 0.0,
    }
    expected_saved = queue_df.apply(
        lambda row: row["churn_probability"] * save_rates.get(row["recommended_action"], 0.0),
        axis=1,
    ).sum()
    baseline_saved = queue_df["churn_probability"].mean() * 0.04 * len(queue_df)
    if baseline_saved == 0:
        return 0.0
    return float((expected_saved - baseline_saved) / baseline_saved * 100)


def build_model(random_state: int = 42) -> XGBClassifier:
    return XGBClassifier(
        n_estimators=160,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.85,
        reg_lambda=1.8,
        min_child_weight=3,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=random_state,
        n_jobs=1,
        verbosity=0,
    )


def train_and_export(feature_df: pd.DataFrame, artifact_dir: Path) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)

    X_full = model_input_frame(feature_df)
    y_full = feature_df[TARGET_COLUMN].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X_full,
        y_full,
        test_size=0.25,
        random_state=42,
        stratify=y_full,
    )

    model = build_model()
    model.fit(X_train, y_train)

    y_score = model.predict_proba(X_test)[:, 1]
    threshold = 0.50
    y_pred = (y_score >= threshold).astype(int)

    metrics = {
        "roc_auc": float(roc_auc_score(y_test, y_score)),
        "pr_auc": float(average_precision_score(y_test, y_score)),
        "precision": float(precision_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred)),
        "precision_at_10_pct": precision_at_k(y_test, y_score, 0.10),
        "recall_at_10_pct": recall_at_k(y_test, y_score, 0.10),
    }

    scored_full = feature_df.copy()
    scored_full["churn_probability"] = model.predict_proba(X_full)[:, 1]

    decisions = scored_full.apply(
        lambda row: choose_intervention(
            score=float(row["churn_probability"]),
            monthly_recurring_revenue=float(row["monthly_recurring_revenue"]),
            unresolved_tickets=int(row["unresolved_tickets"]),
            payment_failures_90d=int(row["payment_failures_90d"]),
            feature_adoption_score=float(row["feature_adoption_score"]),
            plan_tier=str(row["plan_tier"]),
        ),
        axis=1,
    )
    scored_full["risk_tier"] = [d.risk_tier for d in decisions]
    scored_full["recommended_action"] = [d.recommended_action for d in decisions]
    scored_full["priority"] = [d.priority for d in decisions]
    scored_full["owner"] = [d.owner for d in decisions]
    scored_full["intervention_rationale"] = [d.rationale for d in decisions]

    top_queue = scored_full.sort_values(
        ["churn_probability", "monthly_recurring_revenue"],
        ascending=[False, False],
    ).head(200)

    metrics["simulated_retention_uplift"] = simulated_retention_uplift(top_queue)

    model.save_model(artifact_dir / "model.json")

    metadata = {
        "feature_columns": list(X_full.columns),
        "threshold": threshold,
        "target_column": TARGET_COLUMN,
        "categorical_encoding": "pandas.get_dummies",
        "risk_tier_thresholds": {"critical": 0.80, "high": 0.65, "medium": 0.40, "low": 0.0},
    }
    (artifact_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
    (artifact_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))

    cm = confusion_matrix(y_test, y_pred)
    confusion_payload = {
        "index": ["actual_0", "actual_1"],
        "columns": ["pred_0", "pred_1"],
        "matrix": cm.tolist(),
    }
    (artifact_dir / "confusion_matrix.json").write_text(json.dumps(confusion_payload, indent=2))
    top_queue.to_csv(artifact_dir / "top_risk_accounts.csv", index=False)

    explanations = _export_shap_explanations(model, X_full, scored_full)
    (artifact_dir / "account_explanations.json").write_text(json.dumps(explanations, indent=2))


def _pretty_feature_name(name: str) -> str:
    return name.replace("_", " ")


def _export_shap_explanations(model: XGBClassifier, X_full: pd.DataFrame, scored_full: pd.DataFrame) -> dict[str, dict]:
    explainer = shap.TreeExplainer(model)
    candidate_ids = scored_full.sort_values("churn_probability", ascending=False)["account_id"].head(120).tolist()
    candidate_mask = scored_full["account_id"].isin(candidate_ids)
    candidate_rows = scored_full.loc[candidate_mask].reset_index(drop=True)
    X_subset = X_full.loc[candidate_mask].reset_index(drop=True)

    shap_values = explainer.shap_values(X_subset)
    if isinstance(shap_values, list):
        shap_values = shap_values[1]

    explanations: dict[str, dict] = {}
    for row_idx in range(len(candidate_rows)):
        account = candidate_rows.iloc[row_idx]
        contribution_row = pd.Series(shap_values[row_idx], index=X_subset.columns)
        top_contributors = (
            contribution_row.reindex(contribution_row.abs().sort_values(ascending=False).index)
            .head(5)
        )

        drivers = []
        for feature_name, impact in top_contributors.items():
            value = float(X_subset.iloc[row_idx][feature_name])
            direction = "raises" if float(impact) >= 0 else "reduces"
            drivers.append(
                {
                    "feature": feature_name,
                    "display_name": _pretty_feature_name(feature_name),
                    "feature_value": round(value, 4),
                    "impact": round(float(impact), 5),
                    "direction": direction,
                }
            )

        decision = choose_intervention(
            score=float(account["churn_probability"]),
            monthly_recurring_revenue=float(account["monthly_recurring_revenue"]),
            unresolved_tickets=int(account["unresolved_tickets"]),
            payment_failures_90d=int(account["payment_failures_90d"]),
            feature_adoption_score=float(account["feature_adoption_score"]),
            plan_tier=str(account["plan_tier"]),
        )
        explanations[str(account["account_id"])] = {
            "account_id": str(account["account_id"]),
            "churn_probability": round(float(account["churn_probability"]), 4),
            "risk_tier": risk_tier(float(account["churn_probability"])),
            "recommended_action": decision.recommended_action,
            "priority": decision.priority,
            "rationale": decision.rationale,
            "drivers": drivers,
        }
    return explanations
