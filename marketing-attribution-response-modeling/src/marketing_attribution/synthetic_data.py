from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
import pandas as pd


CHANNELS = [
    "paid_search",
    "paid_social",
    "display",
    "affiliate",
    "email",
    "organic_search",
    "direct",
]
PAID_CHANNELS = ["paid_search", "paid_social", "display", "affiliate", "email"]
SEGMENTS = ["new", "active", "power"]
DEVICES = ["mobile", "desktop", "tablet"]
PRODUCTS = ["essentials", "premium", "seasonal"]
REGIONS = ["North America", "Europe", "APAC", "LATAM"]

CHANNEL_CPC = {
    "paid_search": 0.9,
    "paid_social": 0.35,
    "display": 0.08,
    "affiliate": 0.65,
    "email": 0.02,
    "organic_search": 0.0,
    "direct": 0.0,
}
CHANNEL_WEIGHTS = {
    "paid_search": 0.50,
    "paid_social": 0.20,
    "display": 0.10,
    "affiliate": 0.28,
    "email": 0.36,
    "organic_search": 0.42,
    "direct": 0.48,
}
AOV_BY_PRODUCT = {"essentials": 180.0, "premium": 330.0, "seasonal": 250.0}

RESPONSE_PARAMS = {
    "paid_search": {"alpha": 190.0, "beta": 0.00115, "aov": 210.0, "base": 4200},
    "paid_social": {"alpha": 150.0, "beta": 0.00085, "aov": 185.0, "base": 3600},
    "display": {"alpha": 95.0, "beta": 0.00055, "aov": 160.0, "base": 2500},
    "affiliate": {"alpha": 112.0, "beta": 0.00095, "aov": 195.0, "base": 2800},
    "email": {"alpha": 108.0, "beta": 0.00155, "aov": 175.0, "base": 1700},
}


@dataclass(slots=True)
class SyntheticBundle:
    touchpoints: pd.DataFrame
    journeys: pd.DataFrame
    daily_spend: pd.DataFrame


def _sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-x))


def generate_touchpoint_data(n_users: int = 12000, seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    start = pd.Timestamp("2026-01-01")

    touch_rows = []
    journey_rows = []

    for user_idx in range(1, n_users + 1):
        user_id = f"user-{user_idx:06d}"
        journey_id = f"journey-{user_idx:06d}"
        segment = rng.choice(SEGMENTS, p=[0.34, 0.47, 0.19])
        device = rng.choice(DEVICES, p=[0.57, 0.34, 0.09])
        product = rng.choice(PRODUCTS, p=[0.45, 0.34, 0.21])
        region = rng.choice(REGIONS, p=[0.43, 0.25, 0.22, 0.10])

        path_length = int(rng.integers(2, 8))
        day_offsets = np.sort(rng.integers(0, 90, size=path_length))

        channels = []
        for pos in range(path_length):
            if pos == path_length - 1:
                probs = np.array([0.19, 0.12, 0.06, 0.11, 0.18, 0.16, 0.18])
            elif pos == 0:
                probs = np.array([0.24, 0.23, 0.17, 0.12, 0.07, 0.12, 0.05])
            else:
                probs = np.array([0.22, 0.19, 0.13, 0.11, 0.12, 0.12, 0.11])
            channels.append(rng.choice(CHANNELS, p=probs / probs.sum()))

        clicks_by_channel = {ch: 0 for ch in CHANNELS}
        touches_by_channel = {ch: 0 for ch in CHANNELS}
        total_spend = 0.0

        for pos, (day_offset, channel) in enumerate(zip(day_offsets, channels), start=1):
            touches_by_channel[channel] += 1
            impressions = int(max(1, rng.normal(520 if channel in PAID_CHANNELS else 1, 140))) if channel in PAID_CHANNELS else 1
            if channel in PAID_CHANNELS:
                ctr = {
                    "paid_search": 0.058,
                    "paid_social": 0.026,
                    "display": 0.012,
                    "affiliate": 0.032,
                    "email": 0.067,
                }[channel]
                clicks = int(max(1, rng.poisson(max(impressions * ctr, 1))))
                spend = round(clicks * CHANNEL_CPC[channel], 2)
            elif channel == "organic_search":
                clicks = int(rng.integers(1, 4))
                spend = 0.0
            else:
                clicks = int(rng.integers(1, 3))
                spend = 0.0

            clicks_by_channel[channel] += clicks
            total_spend += spend
            event_time = start + pd.Timedelta(days=int(day_offset)) + pd.Timedelta(hours=int(rng.integers(0, 24)))
            touch_rows.append(
                {
                    "user_id": user_id,
                    "journey_id": journey_id,
                    "event_time": event_time.isoformat(),
                    "path_position": pos,
                    "channel": channel,
                    "segment": segment,
                    "device": device,
                    "region": region,
                    "product_category": product,
                    "impressions": impressions,
                    "clicks": clicks,
                    "spend": spend,
                    "is_paid": int(channel in PAID_CHANNELS),
                }
            )

        score = -4.55
        for ch in CHANNELS:
            score += CHANNEL_WEIGHTS[ch] * touches_by_channel[ch]
            score += 0.0022 * clicks_by_channel[ch]
        score += {"new": -0.15, "active": 0.12, "power": 0.48}[segment]
        score += {"mobile": -0.08, "desktop": 0.17, "tablet": 0.03}[device]
        score += {"essentials": 0.03, "premium": 0.22, "seasonal": 0.11}[product]
        score += min(path_length, 5) * 0.06
        score += rng.normal(0, 0.35)

        conversion_prob = float(_sigmoid(score))
        converted = int(rng.random() < conversion_prob)
        order_value = 0.0
        if converted:
            base_aov = AOV_BY_PRODUCT[product] * {"new": 0.92, "active": 1.0, "power": 1.22}[segment]
            order_value = round(max(20, rng.normal(base_aov, base_aov * 0.17)), 2)

        journey_rows.append(
            {
                "user_id": user_id,
                "journey_id": journey_id,
                "segment": segment,
                "device": device,
                "region": region,
                "product_category": product,
                "path_length": path_length,
                "total_spend": round(total_spend, 2),
                "first_touch": channels[0],
                "last_touch": channels[-1],
                "converted": converted,
                "revenue": order_value,
                "conversion_probability": round(conversion_prob, 4),
            }
        )

    return pd.DataFrame(touch_rows), pd.DataFrame(journey_rows)


def generate_daily_spend_panel(days: int = 120, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 7)
    rows = []
    start = pd.Timestamp("2025-11-01")

    for channel, params in RESPONSE_PARAMS.items():
        for offset in range(days):
            date = start + pd.Timedelta(days=offset)
            weekday_factor = 1.06 if date.weekday() in (1, 2, 3) else 0.95
            season_factor = 1.0 + 0.09 * math.sin(offset / 8.0)
            spend = params["base"] * weekday_factor * season_factor + rng.normal(0, params["base"] * 0.08)
            spend = max(350.0, spend)
            expected_conversions = params["alpha"] * (1 - math.exp(-params["beta"] * spend))
            conversions = max(0.0, expected_conversions * weekday_factor * season_factor + rng.normal(0, expected_conversions * 0.08))
            revenue = conversions * params["aov"]
            rows.append(
                {
                    "date": date.date().isoformat(),
                    "channel": channel,
                    "spend": round(spend, 2),
                    "conversions": round(conversions, 2),
                    "revenue": round(revenue, 2),
                }
            )

    return pd.DataFrame(rows)


def generate_bundle(seed: int = 42) -> SyntheticBundle:
    touchpoints, journeys = generate_touchpoint_data(seed=seed)
    daily_spend = generate_daily_spend_panel(seed=seed)
    return SyntheticBundle(touchpoints=touchpoints, journeys=journeys, daily_spend=daily_spend)
