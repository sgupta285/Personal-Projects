"""
Core Engagement Metrics.

Computes:
- DAU / WAU / MAU (daily/weekly/monthly active users)
- DAU/MAU stickiness ratio
- Session frequency, depth, and duration
- Feature adoption rates and power user analysis
- L7/L28 (days active in last 7/28)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()


@dataclass
class EngagementSnapshot:
    date: pd.Timestamp
    dau: int
    wau: int
    mau: int
    stickiness: float          # DAU/MAU
    avg_sessions_per_dau: float
    avg_duration_sec: float
    avg_page_views: float
    total_events: int


@dataclass
class FeatureAdoption:
    feature: str
    total_users: int
    adoption_rate: float       # % of MAU who used it
    avg_uses_per_user: float
    power_user_pct: float      # Top 10% usage share
    retention_correlation: float


class EngagementAnalyzer:
    """Compute engagement metrics from session data."""

    def compute_dau_wau_mau(
        self, sessions_df: pd.DataFrame, date_col: str = "date", user_col: str = "user_id"
    ) -> pd.DataFrame:
        """Compute DAU, WAU, MAU time series."""
        sessions = sessions_df.copy()
        sessions[date_col] = pd.to_datetime(sessions[date_col])

        daily_active = sessions.groupby(date_col)[user_col].nunique().reset_index()
        daily_active.columns = ["date", "dau"]

        # WAU: unique users in rolling 7-day window
        all_dates = pd.date_range(daily_active["date"].min(), daily_active["date"].max())
        result = pd.DataFrame({"date": all_dates})

        dau_map = dict(zip(daily_active["date"], daily_active["dau"]))
        result["dau"] = result["date"].map(dau_map).fillna(0).astype(int)

        # Rolling unique users (approximate via daily sets)
        user_sets_by_date = sessions.groupby(date_col)[user_col].apply(set).to_dict()

        wau_vals = []
        mau_vals = []
        for d in all_dates:
            # WAU
            wau_users = set()
            for offset in range(7):
                check_date = d - pd.Timedelta(days=offset)
                wau_users |= user_sets_by_date.get(check_date, set())
            wau_vals.append(len(wau_users))

            # MAU
            mau_users = set()
            for offset in range(30):
                check_date = d - pd.Timedelta(days=offset)
                mau_users |= user_sets_by_date.get(check_date, set())
            mau_vals.append(len(mau_users))

        result["wau"] = wau_vals
        result["mau"] = mau_vals
        result["stickiness"] = (result["dau"] / result["mau"].clip(lower=1)).round(4)

        return result

    def compute_session_metrics(self, sessions_df: pd.DataFrame) -> pd.DataFrame:
        """Daily session-level metrics."""
        daily = sessions_df.groupby("date").agg(
            total_sessions=("user_id", "count"),
            unique_users=("user_id", "nunique"),
            avg_duration=("duration_sec", "mean"),
            median_duration=("duration_sec", "median"),
            avg_page_views=("page_views", "mean"),
            avg_features=("n_features", "mean"),
        ).reset_index()

        daily["sessions_per_user"] = (daily["total_sessions"] / daily["unique_users"]).round(2)
        return daily

    def compute_feature_adoption(
        self, sessions_df: pd.DataFrame, events_df: pd.DataFrame,
        features: List[str], mau_count: int,
    ) -> List[FeatureAdoption]:
        """Compute adoption rate and engagement depth per feature."""
        results = []
        feature_events = events_df[events_df["event_type"] == "feature_use"]

        for feat in features:
            feat_users = feature_events[feature_events["feature"] == feat]
            n_users = feat_users["user_id"].nunique()
            adoption = n_users / mau_count if mau_count > 0 else 0

            if n_users > 0:
                user_counts = feat_users.groupby("user_id").size()
                avg_uses = user_counts.mean()
                top10_threshold = user_counts.quantile(0.90)
                power_share = user_counts[user_counts >= top10_threshold].sum() / user_counts.sum()
            else:
                avg_uses = 0
                power_share = 0

            results.append(FeatureAdoption(
                feature=feat, total_users=n_users,
                adoption_rate=round(adoption, 4),
                avg_uses_per_user=round(avg_uses, 2),
                power_user_pct=round(power_share, 4),
                retention_correlation=0.0,  # Filled separately
            ))

        results.sort(key=lambda x: x.adoption_rate, reverse=True)
        return results

    def compute_l_metrics(
        self, sessions_df: pd.DataFrame, reference_date: pd.Timestamp
    ) -> pd.DataFrame:
        """Compute L7 and L28 (days active in last 7/28 days) per user."""
        sessions = sessions_df.copy()
        sessions["date"] = pd.to_datetime(sessions["date"])

        last_7 = sessions[sessions["date"] > reference_date - pd.Timedelta(days=7)]
        last_28 = sessions[sessions["date"] > reference_date - pd.Timedelta(days=28)]

        l7 = last_7.groupby("user_id")["date"].nunique().reset_index()
        l7.columns = ["user_id", "L7"]

        l28 = last_28.groupby("user_id")["date"].nunique().reset_index()
        l28.columns = ["user_id", "L28"]

        result = l7.merge(l28, on="user_id", how="outer").fillna(0)
        result["L7"] = result["L7"].astype(int)
        result["L28"] = result["L28"].astype(int)
        return result
