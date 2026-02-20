"""
User Segmentation.

Implements:
- RFM (Recency, Frequency, Monetary) scoring and segmentation
- Behavioral clustering via K-Means on engagement features
"""

import numpy as np
import pandas as pd
from typing import Dict, List
from dataclasses import dataclass
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import structlog

logger = structlog.get_logger()


@dataclass
class RFMSegment:
    segment_name: str
    n_users: int
    pct_of_total: float
    avg_recency: float
    avg_frequency: float
    avg_monetary: float
    avg_rfm_score: float


class RFMSegmenter:
    """Segment users by Recency, Frequency, Monetary value."""

    def compute_rfm(
        self, users_df: pd.DataFrame, sessions_df: pd.DataFrame,
        reference_date: pd.Timestamp = None,
    ) -> pd.DataFrame:
        """Compute RFM scores for each user."""
        sessions = sessions_df.copy()
        sessions["date"] = pd.to_datetime(sessions["date"])

        if reference_date is None:
            reference_date = sessions["date"].max()

        # Recency: days since last active
        last_active = sessions.groupby("user_id")["date"].max().reset_index()
        last_active.columns = ["user_id", "last_date"]
        last_active["recency"] = (reference_date - last_active["last_date"]).dt.days

        # Frequency: number of active days
        frequency = sessions.groupby("user_id")["date"].nunique().reset_index()
        frequency.columns = ["user_id", "frequency"]

        # Monetary: total revenue
        monetary = users_df[["user_id", "total_revenue"]].copy()
        monetary.columns = ["user_id", "monetary"]

        rfm = last_active[["user_id", "recency"]].merge(frequency, on="user_id")
        rfm = rfm.merge(monetary, on="user_id")

        # Score 1-5 for each dimension (quintiles)
        rfm["R_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
        rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
        rfm["M_score"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)

        rfm["RFM_score"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

        # Assign segments
        rfm["segment"] = rfm.apply(self._assign_segment, axis=1)

        return rfm

    @staticmethod
    def _assign_segment(row) -> str:
        r, f, m = row["R_score"], row["F_score"], row["M_score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        elif r >= 4 and f >= 3:
            return "Loyal"
        elif r >= 3 and f <= 2 and m >= 3:
            return "Big Spenders"
        elif r >= 4 and f <= 2:
            return "New Users"
        elif r <= 2 and f >= 3:
            return "At Risk"
        elif r <= 2 and f <= 2 and m >= 3:
            return "Can't Lose"
        elif r <= 2 and f <= 2:
            return "Hibernating"
        else:
            return "Need Attention"

    def segment_summary(self, rfm_df: pd.DataFrame) -> List[RFMSegment]:
        n_total = len(rfm_df)
        results = []
        for seg, group in rfm_df.groupby("segment"):
            results.append(RFMSegment(
                segment_name=seg, n_users=len(group),
                pct_of_total=round(len(group) / n_total * 100, 1),
                avg_recency=round(group["recency"].mean(), 1),
                avg_frequency=round(group["frequency"].mean(), 1),
                avg_monetary=round(group["monetary"].mean(), 2),
                avg_rfm_score=round(group["RFM_score"].mean(), 1),
            ))
        results.sort(key=lambda x: x.avg_rfm_score, reverse=True)
        return results


class BehavioralClusterer:
    """Cluster users by behavioral features using K-Means."""

    def cluster_users(
        self, users_df: pd.DataFrame, sessions_df: pd.DataFrame,
        n_clusters: int = 5,
    ) -> pd.DataFrame:
        """Cluster users based on engagement features."""
        sessions = sessions_df.copy()

        # Aggregate session features per user
        user_features = sessions.groupby("user_id").agg(
            total_sessions=("date", "count"),
            unique_days=("date", "nunique"),
            avg_duration=("duration_sec", "mean"),
            avg_page_views=("page_views", "mean"),
            avg_features=("n_features", "mean"),
            total_duration=("duration_sec", "sum"),
        ).reset_index()

        user_features = user_features.merge(
            users_df[["user_id", "total_revenue", "is_subscriber"]], on="user_id"
        )
        user_features["is_subscriber"] = user_features["is_subscriber"].astype(int)

        # Normalize
        feature_cols = ["total_sessions", "unique_days", "avg_duration",
                        "avg_page_views", "avg_features", "total_revenue", "is_subscriber"]
        X = user_features[feature_cols].fillna(0).values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        user_features["cluster"] = kmeans.fit_predict(X_scaled)

        # Label clusters by engagement level
        cluster_engagement = user_features.groupby("cluster")["total_sessions"].mean()
        rank_map = {c: r for r, c in enumerate(cluster_engagement.sort_values().index)}
        labels = ["Dormant", "Casual", "Regular", "Engaged", "Power User"]
        user_features["cluster_label"] = user_features["cluster"].map(
            lambda c: labels[min(rank_map.get(c, 0), len(labels) - 1)]
        )

        return user_features
