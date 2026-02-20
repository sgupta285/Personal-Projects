"""
Funnel Analysis & Revenue Metrics.

Funnel:
- Stage-by-stage conversion rates
- Drop-off analysis
- Segment-level funnel comparison

Revenue:
- ARPU / ARPPU (average revenue per user / paying user)
- LTV estimation via BG/NBD-like simplified model
- Revenue cohort analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass
import structlog

from src.config import config

logger = structlog.get_logger()


# ============================================================
# FUNNEL ANALYSIS
# ============================================================

@dataclass
class FunnelStage:
    stage: str
    users: int
    rate_from_previous: float   # Conversion from prior stage
    rate_from_top: float        # Conversion from top of funnel
    drop_off_pct: float         # % lost at this stage


@dataclass
class FunnelResult:
    stages: List[FunnelStage]
    overall_conversion: float
    biggest_drop_stage: str
    biggest_drop_pct: float


class FunnelAnalyzer:
    """Compute funnel conversion rates and identify bottlenecks."""

    def analyze_funnel(
        self, users_df: pd.DataFrame, funnel_stages: List[str],
        stage_columns: Dict[str, str] = None,
    ) -> FunnelResult:
        """
        Analyze conversion funnel.

        Args:
            users_df: User-level data
            funnel_stages: Ordered list of stage names
            stage_columns: Mapping of stage name → boolean column in users_df
                          If None, uses onboarding_depth for built-in funnel.
        """
        n_total = len(users_df)
        stages = []
        prev_count = n_total
        max_drop = 0
        max_drop_stage = ""

        for i, stage in enumerate(funnel_stages):
            if stage_columns and stage in stage_columns:
                count = users_df[stage_columns[stage]].sum()
            else:
                # Use onboarding depth
                count = (users_df["onboarding_depth"] > i).sum()

            rate_prev = count / prev_count if prev_count > 0 else 0
            rate_top = count / n_total if n_total > 0 else 0
            drop = 1 - rate_prev

            if i > 0 and drop > max_drop:
                max_drop = drop
                max_drop_stage = stage

            stages.append(FunnelStage(
                stage=stage, users=int(count),
                rate_from_previous=round(rate_prev, 4),
                rate_from_top=round(rate_top, 4),
                drop_off_pct=round(drop * 100, 1),
            ))
            prev_count = count

        overall = stages[-1].rate_from_top if stages else 0

        return FunnelResult(
            stages=stages, overall_conversion=round(overall, 4),
            biggest_drop_stage=max_drop_stage,
            biggest_drop_pct=round(max_drop * 100, 1),
        )

    def funnel_by_segment(
        self, users_df: pd.DataFrame, funnel_stages: List[str],
        segment_col: str,
    ) -> Dict[str, FunnelResult]:
        """Compute funnel for each segment."""
        results = {}
        for seg in users_df[segment_col].unique():
            seg_users = users_df[users_df[segment_col] == seg]
            results[str(seg)] = self.analyze_funnel(seg_users, funnel_stages)
        return results


# ============================================================
# REVENUE METRICS
# ============================================================

@dataclass
class RevenueMetrics:
    total_revenue: float
    arpu: float                # Avg revenue per user
    arppu: float               # Avg revenue per paying user
    paying_user_pct: float
    avg_purchases_per_payer: float
    avg_order_value: float
    ltv_30d: float
    ltv_90d: float
    ltv_projected: float       # Projected using decay model


class RevenueAnalyzer:
    """Compute revenue and LTV metrics."""

    def compute_revenue_metrics(
        self, users_df: pd.DataFrame, events_df: pd.DataFrame,
    ) -> RevenueMetrics:
        """Compute ARPU, ARPPU, and purchase metrics."""
        n_users = len(users_df)
        total_rev = users_df["total_revenue"].sum()
        paying = users_df[users_df["total_revenue"] > 0]
        n_paying = len(paying)

        purchases = events_df[events_df["event_type"] == "purchase"]
        n_purchases = len(purchases)

        arpu = total_rev / n_users if n_users > 0 else 0
        arppu = total_rev / n_paying if n_paying > 0 else 0
        pay_pct = n_paying / n_users if n_users > 0 else 0
        avg_purchases = n_purchases / n_paying if n_paying > 0 else 0
        aov = purchases["revenue"].mean() if len(purchases) > 0 else 0

        # LTV by cohort time windows
        ltv_30d = self._compute_ltv_window(users_df, events_df, 30)
        ltv_90d = self._compute_ltv_window(users_df, events_df, 90)
        ltv_proj = self._project_ltv(users_df, events_df)

        return RevenueMetrics(
            total_revenue=round(total_rev, 2),
            arpu=round(arpu, 2), arppu=round(arppu, 2),
            paying_user_pct=round(pay_pct, 4),
            avg_purchases_per_payer=round(avg_purchases, 2),
            avg_order_value=round(aov, 2),
            ltv_30d=round(ltv_30d, 2),
            ltv_90d=round(ltv_90d, 2),
            ltv_projected=round(ltv_proj, 2),
        )

    def _compute_ltv_window(
        self, users_df: pd.DataFrame, events_df: pd.DataFrame, days: int
    ) -> float:
        """Compute average revenue within first N days of signup."""
        users = users_df.copy()
        events = events_df.copy()
        users["signup_date"] = pd.to_datetime(users["signup_date"])
        events["date"] = pd.to_datetime(events["date"])

        revenue_events = events[events["revenue"] > 0].merge(
            users[["user_id", "signup_date"]], on="user_id"
        )
        revenue_events["days_since_signup"] = (
            revenue_events["date"] - revenue_events["signup_date"]
        ).dt.days

        # Only users with enough history
        max_date = events["date"].max()
        eligible = users[users["signup_date"] <= max_date - pd.Timedelta(days=days)]
        if len(eligible) == 0:
            return 0.0

        eligible_ids = set(eligible["user_id"])
        window_rev = revenue_events[
            (revenue_events["user_id"].isin(eligible_ids)) &
            (revenue_events["days_since_signup"] <= days)
        ]

        total = window_rev["revenue"].sum()
        return total / len(eligible)

    def _project_ltv(
        self, users_df: pd.DataFrame, events_df: pd.DataFrame,
        projection_months: int = 24,
    ) -> float:
        """Project LTV using observed revenue decay curve."""
        users = users_df.copy()
        events = events_df[events_df["revenue"] > 0].copy()
        users["signup_date"] = pd.to_datetime(users["signup_date"])
        events["date"] = pd.to_datetime(events["date"])

        events = events.merge(users[["user_id", "signup_date"]], on="user_id")
        events["month"] = ((events["date"] - events["signup_date"]).dt.days // 30).clip(lower=0)

        # Monthly ARPU by cohort month
        monthly = events.groupby("month")["revenue"].sum()
        n_users = len(users)

        if len(monthly) < 2:
            return 0.0

        # Extrapolate using observed decay
        months = monthly.index.values
        arpu_monthly = (monthly / n_users).values

        # Simple exponential decay fit
        if len(months) >= 3:
            log_arpu = np.log(np.clip(arpu_monthly, 0.01, None))
            coeffs = np.polyfit(months, log_arpu, 1)
            decay_rate = coeffs[0]

            projected_ltv = 0
            discount_monthly = config.ltv.discount_rate_annual / 12
            for m in range(projection_months):
                monthly_rev = np.exp(coeffs[1] + decay_rate * m)
                projected_ltv += monthly_rev / (1 + discount_monthly) ** m
        else:
            projected_ltv = arpu_monthly.mean() * projection_months

        return float(projected_ltv)

    def revenue_cohort_table(
        self, users_df: pd.DataFrame, events_df: pd.DataFrame,
        cohort_freq: str = "M",
    ) -> pd.DataFrame:
        """Cumulative revenue per cohort over time."""
        users = users_df.copy()
        events = events_df[events_df["revenue"] > 0].copy()
        users["signup_date"] = pd.to_datetime(users["signup_date"])
        events["date"] = pd.to_datetime(events["date"])

        users["cohort"] = users["signup_date"].dt.to_period(cohort_freq).astype(str)
        events = events.merge(users[["user_id", "signup_date", "cohort"]], on="user_id")
        events["period"] = ((events["date"] - events["signup_date"]).dt.days // 30).clip(lower=0)

        cohort_sizes = users.groupby("cohort")["user_id"].nunique()
        rev = events.groupby(["cohort", "period"])["revenue"].sum().reset_index()
        pivot = rev.pivot(index="cohort", columns="period", values="revenue").fillna(0)

        # Cumulative
        cum_pivot = pivot.cumsum(axis=1)
        # Per-user
        per_user = cum_pivot.div(cohort_sizes, axis=0).round(2)

        return per_user
