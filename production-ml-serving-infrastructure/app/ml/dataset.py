from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.schemas.prediction import FEATURE_ORDER


@dataclass
class DatasetBundle:
    frame: pd.DataFrame
    features: np.ndarray
    labels: np.ndarray


def make_synthetic_dataset(rows: int = 5000, seed: int = 42) -> DatasetBundle:
    rng = np.random.default_rng(seed)
    random.seed(seed)
    account_tenure_days = rng.integers(1, 720, size=rows)
    avg_session_seconds = rng.normal(loc=480, scale=180, size=rows).clip(30, 1800)
    prior_purchases = rng.poisson(lam=4, size=rows).clip(0, 40)
    cart_additions_7d = rng.poisson(lam=6, size=rows).clip(0, 30)
    email_click_rate = rng.beta(a=2, b=5, size=rows)
    discount_sensitivity = rng.beta(a=3, b=3, size=rows)
    inventory_score = rng.uniform(0.35, 1.0, size=rows)
    device_trust_score = rng.uniform(0.40, 1.0, size=rows)

    logits = (
        -2.2
        + account_tenure_days / 900
        + avg_session_seconds / 1200
        + prior_purchases / 9
        + cart_additions_7d / 8
        + 1.4 * email_click_rate
        + 0.8 * discount_sensitivity
        + 0.9 * inventory_score
        + 0.7 * device_trust_score
    )
    probs = 1 / (1 + np.exp(-logits))
    labels = rng.binomial(1, probs.clip(0.03, 0.97))

    frame = pd.DataFrame(
        {
            "account_tenure_days": account_tenure_days,
            "avg_session_seconds": avg_session_seconds,
            "prior_purchases": prior_purchases,
            "cart_additions_7d": cart_additions_7d,
            "email_click_rate": email_click_rate,
            "discount_sensitivity": discount_sensitivity,
            "inventory_score": inventory_score,
            "device_trust_score": device_trust_score,
            "label": labels,
        }
    )
    features = frame[FEATURE_ORDER].to_numpy(dtype=np.float32)
    return DatasetBundle(frame=frame, features=features, labels=labels.astype(np.float32))
