from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

PLAN_MRR = {
    "starter": (150, 400),
    "growth": (450, 1800),
    "scale": (1800, 4500),
    "enterprise": (4500, 12000),
}

REGIONS = ["North America", "Europe", "APAC", "LATAM"]
INDUSTRIES = ["Fintech", "Ecommerce", "Healthcare", "SaaS", "Education", "Logistics"]
PLAN_TIERS = list(PLAN_MRR)
CONTRACT_TYPES = ["monthly", "annual", "multi_year"]


@dataclass(slots=True)
class GeneratorConfig:
    n_customers: int = 3500
    seed: int = 42


def _bounded_normal(
    rng: np.random.Generator,
    mean: float,
    sd: float,
    low: float,
    high: float,
    size: int,
) -> np.ndarray:
    values = rng.normal(mean, sd, size)
    return np.clip(values, low, high)


def generate_dataset(n_customers: int = 3500, seed: int = 42) -> pd.DataFrame:
    cfg = GeneratorConfig(n_customers=n_customers, seed=seed)
    rng = np.random.default_rng(cfg.seed)

    plan_tier = rng.choice(PLAN_TIERS, size=cfg.n_customers, p=[0.34, 0.33, 0.22, 0.11])
    contract_type = rng.choice(CONTRACT_TYPES, size=cfg.n_customers, p=[0.43, 0.45, 0.12])
    region = rng.choice(REGIONS, size=cfg.n_customers, p=[0.42, 0.23, 0.24, 0.11])
    industry = rng.choice(INDUSTRIES, size=cfg.n_customers)

    seat_count = []
    mrr = []
    for plan in plan_tier:
        low, high = PLAN_MRR[plan]
        seats = {
            "starter": rng.integers(2, 12),
            "growth": rng.integers(10, 40),
            "scale": rng.integers(25, 120),
            "enterprise": rng.integers(80, 450),
        }[plan]
        seat_count.append(int(seats))
        mrr.append(float(rng.uniform(low, high)))

    seat_count = np.array(seat_count)
    mrr = np.array(mrr).round(2)

    tenure_months = np.clip(rng.gamma(shape=2.4, scale=8.5, size=cfg.n_customers), 1, 84).round().astype(int)
    days_since_last_activity = np.clip(rng.gamma(shape=2.0, scale=8.0, size=cfg.n_customers), 0, 90).round().astype(int)

    prev_sessions = _bounded_normal(rng, mean=10, sd=4, low=0.2, high=25, size=cfg.n_customers)
    session_decay = rng.normal(0, 2.3, cfg.n_customers)
    avg_weekly_sessions_30d = np.clip(prev_sessions + session_decay - (days_since_last_activity / 25), 0.05, 30).round(2)
    avg_weekly_sessions_prev_30d = prev_sessions.round(2)

    transactions_prev_30d = np.clip(
        prev_sessions * rng.uniform(4, 9, cfg.n_customers) + rng.normal(0, 8, cfg.n_customers),
        0,
        None,
    ).round().astype(int)
    transactions_30d = np.clip(
        avg_weekly_sessions_30d * rng.uniform(4, 9, cfg.n_customers) + rng.normal(0, 8, cfg.n_customers),
        0,
        None,
    ).round().astype(int)

    support_tickets_90d = np.clip(rng.poisson(lam=np.maximum(seat_count / 18, 1.0)), 0, 25)
    unresolved_tickets = np.minimum(support_tickets_90d, rng.binomial(support_tickets_90d, p=0.28))
    payment_failures_90d = rng.binomial(3, p=np.where(contract_type == "monthly", 0.22, 0.08))
    plan_change_count_180d = rng.poisson(lam=np.where(contract_type == "monthly", 1.2, 0.5))
    nps_score = _bounded_normal(rng, mean=28, sd=26, low=-100, high=100, size=cfg.n_customers).round(0)
    csat_score = _bounded_normal(rng, mean=4.0, sd=0.7, low=1.0, high=5.0, size=cfg.n_customers).round(2)
    admin_logins_30d = np.clip(
        seat_count * rng.uniform(0.3, 0.9, cfg.n_customers) + rng.normal(0, 3, cfg.n_customers),
        1,
        None,
    ).round().astype(int)
    api_calls_30d = np.clip(
        seat_count * rng.uniform(30, 260, cfg.n_customers) + rng.normal(0, 1000, cfg.n_customers),
        0,
        None,
    ).round().astype(int)
    feature_adoption_score = _bounded_normal(rng, mean=0.63, sd=0.18, low=0.05, high=1.0, size=cfg.n_customers).round(3)
    onboarding_completion_pct = _bounded_normal(rng, mean=0.79, sd=0.16, low=0.1, high=1.0, size=cfg.n_customers).round(3)
    training_sessions_attended = np.clip(rng.poisson(lam=np.where(plan_tier == "enterprise", 3.2, 1.4)), 0, 8)
    auto_renew = rng.random(cfg.n_customers) < np.where(contract_type == "monthly", 0.45, 0.82)
    last_marketing_touch_days = np.clip(rng.gamma(shape=2.0, scale=11.0, size=cfg.n_customers), 0, 120).round().astype(int)

    engagement_delta = avg_weekly_sessions_30d - avg_weekly_sessions_prev_30d
    transaction_delta = transactions_30d - transactions_prev_30d
    monthly_flag = (contract_type == "monthly").astype(float)
    enterprise_flag = (plan_tier == "enterprise").astype(float)

    logit = (
        -2.25
        + 0.055 * days_since_last_activity
        - 0.18 * engagement_delta
        - 0.015 * transaction_delta
        + 0.38 * unresolved_tickets
        + 0.42 * payment_failures_90d
        + 1.75 * (0.55 - feature_adoption_score)
        + 1.15 * (0.75 - onboarding_completion_pct)
        - 0.018 * nps_score
        - 0.28 * (csat_score - 3.5)
        + 0.22 * plan_change_count_180d
        + 0.65 * monthly_flag
        - 0.7 * auto_renew.astype(float)
        - 0.03 * tenure_months
        - 0.15 * enterprise_flag
        + rng.normal(0, 0.6, cfg.n_customers)
    )

    churn_probability = 1 / (1 + np.exp(-logit))
    churned_60d = rng.binomial(1, p=np.clip(churn_probability, 0.01, 0.98))

    signup_days_ago = (tenure_months * 30 + rng.integers(0, 25, size=cfg.n_customers)).astype(int)
    snapshot_date = pd.Timestamp("2026-03-01")
    signup_date = snapshot_date - pd.to_timedelta(signup_days_ago, unit="D")

    df = pd.DataFrame(
        {
            "account_id": [f"acct-{i:05d}" for i in range(1, cfg.n_customers + 1)],
            "snapshot_date": snapshot_date.date().isoformat(),
            "signup_date": signup_date.date.astype(str),
            "plan_tier": plan_tier,
            "contract_type": contract_type,
            "region": region,
            "industry": industry,
            "monthly_recurring_revenue": mrr,
            "seat_count": seat_count,
            "tenure_months": tenure_months,
            "days_since_last_activity": days_since_last_activity,
            "avg_weekly_sessions_30d": avg_weekly_sessions_30d,
            "avg_weekly_sessions_prev_30d": avg_weekly_sessions_prev_30d,
            "transactions_30d": transactions_30d,
            "transactions_prev_30d": transactions_prev_30d,
            "support_tickets_90d": support_tickets_90d,
            "unresolved_tickets": unresolved_tickets,
            "payment_failures_90d": payment_failures_90d,
            "plan_change_count_180d": plan_change_count_180d,
            "nps_score": nps_score,
            "csat_score": csat_score,
            "admin_logins_30d": admin_logins_30d,
            "api_calls_30d": api_calls_30d,
            "feature_adoption_score": feature_adoption_score,
            "onboarding_completion_pct": onboarding_completion_pct,
            "training_sessions_attended": training_sessions_attended,
            "auto_renew": auto_renew,
            "last_marketing_touch_days": last_marketing_touch_days,
            "churned_60d": churned_60d,
        }
    )
    return df


def save_raw_dataset(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
