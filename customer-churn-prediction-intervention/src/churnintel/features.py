from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

CATEGORICAL_COLUMNS = ["plan_tier", "contract_type", "region", "industry"]
TARGET_COLUMN = "churned_60d"
IDENTIFIER_COLUMNS = ["account_id"]


def build_feature_table(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()
    df["engagement_delta"] = df["avg_weekly_sessions_30d"] - df["avg_weekly_sessions_prev_30d"]
    df["transaction_delta"] = df["transactions_30d"] - df["transactions_prev_30d"]
    df["activity_ratio"] = np.where(
        df["avg_weekly_sessions_prev_30d"] > 0,
        df["avg_weekly_sessions_30d"] / df["avg_weekly_sessions_prev_30d"],
        df["avg_weekly_sessions_30d"],
    )
    df["ticket_burden"] = df["support_tickets_90d"] / df["seat_count"].clip(lower=1) * 10
    df["unresolved_ticket_rate"] = df["unresolved_tickets"] / df["support_tickets_90d"].clip(lower=1)
    df["mrr_per_seat"] = df["monthly_recurring_revenue"] / df["seat_count"].clip(lower=1)
    df["usage_intensity"] = (df["transactions_30d"] + df["api_calls_30d"] / 100) / df["seat_count"].clip(lower=1)
    df["health_score"] = (
        0.35 * (1 - df["days_since_last_activity"].clip(0, 60) / 60)
        + 0.20 * df["feature_adoption_score"]
        + 0.15 * df["onboarding_completion_pct"]
        + 0.15 * (df["csat_score"] / 5)
        + 0.15 * ((df["nps_score"] + 100) / 200)
    ).round(4)

    ordered_columns = [
        "account_id",
        "plan_tier",
        "contract_type",
        "region",
        "industry",
        "monthly_recurring_revenue",
        "seat_count",
        "tenure_months",
        "days_since_last_activity",
        "avg_weekly_sessions_30d",
        "avg_weekly_sessions_prev_30d",
        "engagement_delta",
        "activity_ratio",
        "transactions_30d",
        "transactions_prev_30d",
        "transaction_delta",
        "support_tickets_90d",
        "unresolved_tickets",
        "ticket_burden",
        "unresolved_ticket_rate",
        "payment_failures_90d",
        "plan_change_count_180d",
        "nps_score",
        "csat_score",
        "admin_logins_30d",
        "api_calls_30d",
        "feature_adoption_score",
        "onboarding_completion_pct",
        "training_sessions_attended",
        "auto_renew",
        "mrr_per_seat",
        "usage_intensity",
        "health_score",
        "last_marketing_touch_days",
        "churned_60d",
    ]
    return df[ordered_columns]


def model_input_frame(feature_df: pd.DataFrame) -> pd.DataFrame:
    X = feature_df.drop(columns=[TARGET_COLUMN] + IDENTIFIER_COLUMNS, errors="ignore").copy()
    X["auto_renew"] = X["auto_renew"].astype(int)
    return pd.get_dummies(X, columns=CATEGORICAL_COLUMNS, drop_first=False)


def align_model_frame(frame: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    return frame.reindex(columns=feature_columns, fill_value=0)


def save_feature_table(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
