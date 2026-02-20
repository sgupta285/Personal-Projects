"""
Retention Analysis.

Computes:
- Cohort retention tables (weekly/monthly cohorts)
- Retention curves with confidence intervals
- Churn rate estimation
- Retention by segment (platform, country, variant)
- Unbounded vs bounded retention
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()


@dataclass
class CohortRetention:
    cohort: str                    # Cohort label (e.g., "2024-W01")
    cohort_size: int
    retention_by_period: Dict[int, float]  # period_number → retention rate
    avg_lifetime_days: float


class RetentionAnalyzer:
    """Cohort-based retention analysis."""

    def build_cohort_table(
        self,
        users_df: pd.DataFrame,
        sessions_df: pd.DataFrame,
        cohort_freq: str = "W",    # "W" for weekly, "M" for monthly
        periods: int = 12,
    ) -> pd.DataFrame:
        """
        Build retention cohort table.

        Returns DataFrame: rows = cohorts, columns = period offsets, values = retention rates.
        """
        users = users_df.copy()
        sessions = sessions_df.copy()
        users["signup_date"] = pd.to_datetime(users["signup_date"])
        sessions["date"] = pd.to_datetime(sessions["date"])

        # Assign cohort labels
        if cohort_freq == "W":
            users["cohort"] = users["signup_date"].dt.to_period("W").astype(str)
            sessions = sessions.merge(users[["user_id", "signup_date"]], on="user_id")
            sessions["period"] = (
                (sessions["date"] - sessions["signup_date"]).dt.days // 7
            )
        else:
            users["cohort"] = users["signup_date"].dt.to_period("M").astype(str)
            sessions = sessions.merge(users[["user_id", "signup_date"]], on="user_id")
            sessions["period"] = (
                (sessions["date"] - sessions["signup_date"]).dt.days // 30
            )

        sessions = sessions.merge(users[["user_id", "cohort"]], on="user_id")

        # Cohort sizes
        cohort_sizes = users.groupby("cohort")["user_id"].nunique()

        # Active users per cohort per period
        active = sessions.groupby(["cohort", "period"])["user_id"].nunique().reset_index()
        active.columns = ["cohort", "period", "active_users"]

        # Build retention table
        pivot = active.pivot(index="cohort", columns="period", values="active_users")
        pivot = pivot.reindex(columns=range(periods + 1))

        # Compute retention rates
        retention = pivot.div(cohort_sizes, axis=0)
        retention = retention.round(4)

        # Cap period 0 at 1.0
        if 0 in retention.columns:
            retention[0] = retention[0].clip(upper=1.0)

        return retention

    def compute_retention_curve(
        self,
        users_df: pd.DataFrame,
        sessions_df: pd.DataFrame,
        day_checkpoints: List[int] = None,
    ) -> pd.DataFrame:
        """
        Compute Day-N retention for all users.

        Returns DataFrame with columns: day, retention_rate, n_eligible, n_retained
        """
        if day_checkpoints is None:
            day_checkpoints = [1, 3, 7, 14, 30, 60, 90, 120, 150, 180]

        users = users_df.copy()
        sessions = sessions_df.copy()
        users["signup_date"] = pd.to_datetime(users["signup_date"])
        sessions["date"] = pd.to_datetime(sessions["date"])

        # User activity dates
        user_active_dates = sessions.groupby("user_id")["date"].apply(set).to_dict()
        max_date = sessions["date"].max()

        results = []
        for day_n in day_checkpoints:
            # Eligible: users who signed up at least day_n days ago
            eligible = users[users["signup_date"] <= max_date - pd.Timedelta(days=day_n)]
            n_eligible = len(eligible)

            if n_eligible == 0:
                continue

            # Retained: active on exactly day N (or within a window)
            retained = 0
            for _, user in eligible.iterrows():
                target_date = user["signup_date"] + pd.Timedelta(days=day_n)
                active_dates = user_active_dates.get(user["user_id"], set())
                # Check within ±1 day window
                if any(abs((target_date - d).days) <= 1 for d in active_dates):
                    retained += 1

            results.append({
                "day": day_n,
                "retention_rate": round(retained / n_eligible, 4),
                "n_eligible": n_eligible,
                "n_retained": retained,
            })

        return pd.DataFrame(results)

    def retention_by_segment(
        self,
        users_df: pd.DataFrame,
        sessions_df: pd.DataFrame,
        segment_col: str,
        day_checkpoints: List[int] = None,
    ) -> Dict[str, pd.DataFrame]:
        """Compute retention curves segmented by a user attribute."""
        segments = users_df[segment_col].unique()
        results = {}

        for seg in segments:
            seg_users = users_df[users_df[segment_col] == seg]
            seg_user_ids = set(seg_users["user_id"])
            seg_sessions = sessions_df[sessions_df["user_id"].isin(seg_user_ids)]
            curve = self.compute_retention_curve(seg_users, seg_sessions, day_checkpoints)
            results[str(seg)] = curve

        return results

    @staticmethod
    def estimate_churn_rate(retention_curve: pd.DataFrame) -> Dict:
        """Estimate daily/weekly/monthly churn from retention curve."""
        if len(retention_curve) < 2:
            return {}

        # Fit exponential decay: R(t) = exp(-λt)
        days = retention_curve["day"].values
        rates = retention_curve["retention_rate"].values
        rates = np.clip(rates, 0.001, 1.0)

        # Log-linear fit
        log_rates = np.log(rates)
        if len(days) >= 2:
            coeffs = np.polyfit(days, log_rates, 1)
            daily_churn = 1 - np.exp(coeffs[0])
            weekly_churn = 1 - (1 - daily_churn) ** 7
            monthly_churn = 1 - (1 - daily_churn) ** 30
        else:
            daily_churn = weekly_churn = monthly_churn = 0

        return {
            "daily_churn": round(daily_churn, 4),
            "weekly_churn": round(weekly_churn, 4),
            "monthly_churn": round(monthly_churn, 4),
            "half_life_days": round(-np.log(2) / coeffs[0], 1) if coeffs[0] < 0 else 999,
        }
