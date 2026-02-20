"""
Synthetic Product Event Data Generator.

Generates realistic user behavior data for a SaaS/consumer product:
- User signups with staggered cohorts
- Daily active sessions with feature interactions
- Retention decay (power-law)
- Revenue events (purchases, subscriptions)
- A/B test variant assignment
- Funnel events (onboarding flow)
"""

import numpy as np
import pandas as pd
from typing import Tuple, List
import structlog

from src.config import config

logger = structlog.get_logger()

ONBOARDING_FUNNEL = [
    "signup", "profile_setup", "first_action", "invite_friend", "first_purchase"
]


def generate_product_data(
    n_users: int = 100000,
    n_days: int = 180,
    start_date: str = "2024-01-01",
    seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Generate synthetic product analytics data.

    Returns:
        users_df: User-level (user_id, signup_date, platform, country, variant, ...)
        events_df: Event-level (user_id, date, event_type, feature, revenue)
        sessions_df: Session-level (user_id, date, duration_sec, page_views, features_used)
    """
    np.random.seed(seed)
    dates = pd.date_range(start=start_date, periods=n_days, freq="D")
    cfg = config.data

    platforms = np.random.choice(["ios", "android", "web"], n_users, p=[0.40, 0.35, 0.25])
    countries = np.random.choice(
        ["US", "UK", "DE", "FR", "JP", "BR", "IN", "CA", "AU", "KR"],
        n_users, p=[0.30, 0.12, 0.10, 0.08, 0.08, 0.07, 0.07, 0.06, 0.06, 0.06]
    )
    variants = np.random.choice(["control", "treatment"], n_users, p=[0.50, 0.50])

    # Staggered signups: users join over time
    signup_day_idx = np.zeros(n_users, dtype=int)
    daily_signups = np.random.poisson(cfg.daily_signups_mean, n_days)
    idx = 0
    for day, count in enumerate(daily_signups):
        end = min(idx + count, n_users)
        signup_day_idx[idx:end] = day
        idx = end
        if idx >= n_users:
            break
    # Fill remaining
    signup_day_idx[idx:] = np.random.randint(0, n_days, n_users - idx)

    # User-level engagement propensity (latent)
    engagement_propensity = np.random.beta(2, 5, n_users)  # Right-skewed: most users low engagement

    # Treatment effect: +8% retention improvement
    treatment_boost = np.where(variants == "treatment", 0.08, 0.0)

    user_records = []
    event_records = []
    session_records = []

    for u in range(n_users):
        user_id = f"U{u:06d}"
        signup_day = signup_day_idx[u]
        signup_date = dates[signup_day]
        platform = platforms[u]
        country = countries[u]
        variant = variants[u]
        propensity = engagement_propensity[u] + treatment_boost[u]

        # Platform modifier
        plat_mod = {"ios": 1.1, "android": 0.95, "web": 1.0}[platform]

        is_subscriber = np.random.random() < propensity * 0.3
        total_revenue = 0.0
        total_sessions = 0
        last_active_day = signup_day

        # Onboarding funnel
        onboarding_reached = ["signup"]
        funnel_rates = [1.0, 0.75, 0.55, 0.25, 0.15]
        for i in range(1, len(ONBOARDING_FUNNEL)):
            rate = funnel_rates[i] * (1 + (propensity - 0.3))
            rate = np.clip(rate, 0.01, 0.99)
            if np.random.random() < rate:
                onboarding_reached.append(ONBOARDING_FUNNEL[i])
                event_records.append({
                    "user_id": user_id, "date": signup_date,
                    "event_type": ONBOARDING_FUNNEL[i],
                    "feature": "onboarding", "revenue": 0.0,
                })
            else:
                break

        # Daily activity simulation
        days_since_signup = n_days - signup_day
        for d in range(days_since_signup):
            day_idx = signup_day + d
            if day_idx >= n_days:
                break

            current_date = dates[day_idx]

            # Retention probability decays as power law of days since signup
            days_active = d + 1
            retention_prob = propensity * plat_mod * (days_active ** -0.35)
            retention_prob = np.clip(retention_prob, 0.001, 0.95)

            # Weekend effect
            if current_date.dayofweek >= 5:
                retention_prob *= 1.15

            if np.random.random() > retention_prob:
                continue  # Not active this day

            last_active_day = day_idx
            total_sessions += 1

            # Session details
            duration = max(10, int(np.random.exponential(300) * propensity * 2))
            page_views = max(1, int(np.random.poisson(4 * propensity + 1)))

            # Feature usage
            n_features = min(len(cfg.feature_set), max(1, int(np.random.poisson(2 * propensity + 1))))
            # Weight features by propensity (premium features used more by engaged users)
            feature_weights = np.ones(len(cfg.feature_set))
            feature_weights[-3:] *= propensity * 3  # Premium features
            feature_weights /= feature_weights.sum()
            features_used = np.random.choice(
                cfg.feature_set, size=n_features, replace=False, p=feature_weights
            ).tolist()

            session_records.append({
                "user_id": user_id, "date": current_date,
                "platform": platform, "variant": variant,
                "duration_sec": duration, "page_views": page_views,
                "features_used": ",".join(features_used),
                "n_features": n_features,
            })

            # Events per session
            for feat in features_used:
                event_records.append({
                    "user_id": user_id, "date": current_date,
                    "event_type": "feature_use", "feature": feat, "revenue": 0.0,
                })

            # Purchase event
            if "purchase" in features_used:
                rev = round(np.random.lognormal(2.0, 0.8), 2)
                total_revenue += rev
                event_records.append({
                    "user_id": user_id, "date": current_date,
                    "event_type": "purchase", "feature": "purchase", "revenue": rev,
                })

            # Subscription revenue (monthly)
            if is_subscriber and current_date.day == 1 and d > 0:
                total_revenue += config.ltv.subscription_monthly
                event_records.append({
                    "user_id": user_id, "date": current_date,
                    "event_type": "subscription", "feature": "subscription",
                    "revenue": config.ltv.subscription_monthly,
                })

        # How far through onboarding
        onboarding_depth = len(onboarding_reached)

        user_records.append({
            "user_id": user_id,
            "signup_date": signup_date,
            "platform": platform,
            "country": country,
            "variant": variant,
            "engagement_propensity": round(propensity, 4),
            "is_subscriber": is_subscriber,
            "total_sessions": total_sessions,
            "total_revenue": round(total_revenue, 2),
            "days_active": total_sessions,
            "last_active_date": dates[min(last_active_day, n_days - 1)],
            "onboarding_depth": onboarding_depth,
            "completed_onboarding": onboarding_depth == len(ONBOARDING_FUNNEL),
        })

    users_df = pd.DataFrame(user_records)
    events_df = pd.DataFrame(event_records)
    sessions_df = pd.DataFrame(session_records)

    logger.info("data_generated",
                users=len(users_df), events=len(events_df), sessions=len(sessions_df))
    return users_df, sessions_df, events_df
