from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

CATEGORY_PRICE = {
    "fashion": (28, 92),
    "electronics": (110, 420),
    "beauty": (18, 74),
    "home": (35, 160),
    "sports": (26, 140),
}


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-x))


def generate_sessions(n_sessions: int = 24000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    user_ids = [f"user-{i:05d}" for i in range(1, 8201)]
    started_at = pd.Timestamp("2026-03-01") - pd.to_timedelta(rng.integers(0, 45, size=n_sessions), unit="D")
    started_at = started_at + pd.to_timedelta(rng.integers(0, 24 * 60, size=n_sessions), unit="m")

    device_type = rng.choice(["mobile", "desktop", "tablet"], size=n_sessions, p=[0.58, 0.34, 0.08])
    traffic_channel = rng.choice(["organic_search", "paid_search", "paid_social", "email", "direct", "display"], size=n_sessions, p=[0.23, 0.16, 0.18, 0.12, 0.19, 0.12])
    product_category = rng.choice(["fashion", "electronics", "beauty", "home", "sports"], size=n_sessions)
    user_recency = rng.choice(["new", "active", "lapsed"], size=n_sessions, p=[0.29, 0.48, 0.23])
    variant = rng.choice(["control", "treatment"], size=n_sessions, p=[0.5, 0.5])
    user_id = rng.choice(user_ids, size=n_sessions, replace=True)

    mobile = (device_type == "mobile").astype(float)
    desktop = (device_type == "desktop").astype(float)
    paid_social = (traffic_channel == "paid_social").astype(float)
    email = (traffic_channel == "email").astype(float)
    direct = (traffic_channel == "direct").astype(float)
    active = (user_recency == "active").astype(float)
    lapsed = (user_recency == "lapsed").astype(float)
    electronics = (product_category == "electronics").astype(float)
    fashion = (product_category == "fashion").astype(float)
    treatment = (variant == "treatment").astype(float)

    p_product = _sigmoid(1.45 - 0.25 * mobile + 0.3 * email + 0.25 * direct - 0.2 * lapsed + 0.1 * active)
    p_cart = _sigmoid(-0.55 - 0.45 * mobile - 0.35 * paid_social + 0.22 * email + 0.18 * direct + 0.16 * electronics - 0.22 * lapsed + 0.12 * active + 0.32 * treatment + 0.18 * treatment * mobile + 0.12 * treatment * paid_social)
    p_checkout = _sigmoid(0.28 - 0.22 * mobile + 0.18 * active + 0.1 * fashion + 0.2 * treatment + 0.16 * treatment * mobile)
    p_purchase = _sigmoid(0.62 - 0.18 * mobile + 0.2 * desktop - 0.15 * lapsed + 0.18 * email + 0.12 * direct + 0.08 * treatment)

    landed = np.ones(n_sessions, dtype=int)
    viewed_product = (rng.random(n_sessions) < p_product).astype(int)
    added_to_cart = ((rng.random(n_sessions) < p_cart) & (viewed_product == 1)).astype(int)
    started_checkout = ((rng.random(n_sessions) < p_checkout) & (added_to_cart == 1)).astype(int)
    purchased = ((rng.random(n_sessions) < p_purchase) & (started_checkout == 1)).astype(int)

    order_value = np.zeros(n_sessions)
    for category, (low, high) in CATEGORY_PRICE.items():
        mask = product_category == category
        order_value[mask] = rng.uniform(low, high, size=mask.sum())
    order_value = np.where(purchased == 1, np.round(order_value, 2), 0.0)

    return pd.DataFrame({
        "session_id": [f"sess-{i:06d}" for i in range(1, n_sessions + 1)],
        "user_id": user_id,
        "started_at": pd.to_datetime(started_at),
        "device_type": device_type,
        "traffic_channel": traffic_channel,
        "product_category": product_category,
        "user_recency": user_recency,
        "variant": variant,
        "landed": landed,
        "viewed_product": viewed_product,
        "added_to_cart": added_to_cart,
        "started_checkout": started_checkout,
        "purchased": purchased,
        "order_value": order_value,
    }).sort_values("started_at").reset_index(drop=True)


def expand_events(sessions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in sessions.itertuples(index=False):
        stages = [
            ("landing", 1, row.landed),
            ("product_page", 2, row.viewed_product),
            ("cart", 3, row.added_to_cart),
            ("checkout", 4, row.started_checkout),
            ("purchase", 5, row.purchased),
        ]
        minute_offset = 0
        for stage_name, stage_order, reached in stages:
            if not reached:
                break
            rows.append({
                "session_id": row.session_id,
                "user_id": row.user_id,
                "event_ts": pd.Timestamp(row.started_at) + pd.Timedelta(minutes=minute_offset),
                "stage_name": stage_name,
                "stage_order": stage_order,
                "device_type": row.device_type,
                "traffic_channel": row.traffic_channel,
                "product_category": row.product_category,
                "user_recency": row.user_recency,
                "variant": row.variant,
                "order_value": row.order_value if stage_name == "purchase" else 0.0,
            })
            minute_offset += 2
    return pd.DataFrame(rows)


def save_raw_data(sessions: pd.DataFrame, events: pd.DataFrame, sessions_path: Path, events_path: Path) -> None:
    sessions.to_csv(sessions_path, index=False)
    events.to_csv(events_path, index=False)
