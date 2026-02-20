"""Configuration for Product Metrics & Analytics Framework."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DataConfig:
    n_users: int = 100000
    n_days: int = 180          # 6 months
    start_date: str = "2024-01-01"
    seed: int = 42
    daily_signups_mean: int = 600
    churn_rate_daily: float = 0.003
    base_sessions_per_day: float = 0.35   # Average sessions/user/day for active users
    feature_set: List[str] = field(default_factory=lambda: [
        "feed", "search", "messaging", "notifications", "profile", "settings",
        "premium_feature", "share", "upload", "purchase"
    ])


@dataclass
class ExperimentConfig:
    significance_level: float = 0.05
    power: float = 0.80
    min_detectable_effect: float = 0.02
    correction_method: str = "bonferroni"
    sequential_looks: int = 5
    bayesian_prior_a: float = 1.0
    bayesian_prior_b: float = 1.0


@dataclass
class RetentionConfig:
    cohort_periods: List[int] = field(default_factory=lambda: [1, 3, 7, 14, 30, 60, 90])
    rolling_retention_window: int = 7


@dataclass
class LTVConfig:
    discount_rate_annual: float = 0.10
    projection_months: int = 24
    revenue_per_purchase: float = 9.99
    subscription_monthly: float = 4.99


@dataclass
class Config:
    data: DataConfig = field(default_factory=DataConfig)
    experiment: ExperimentConfig = field(default_factory=ExperimentConfig)
    retention: RetentionConfig = field(default_factory=RetentionConfig)
    ltv: LTVConfig = field(default_factory=LTVConfig)
    output_dir: str = "output"


config = Config()
