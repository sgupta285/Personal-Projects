from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from app.core.config import settings


class FeatureStore:
    def __init__(self) -> None:
        self.offline_path = Path(settings.offline_features_path)
        self.item_metadata_path = Path(settings.item_metadata_path)
        self.user_features: dict[str, dict] = {}
        self.item_features: dict[str, dict] = {}

    def load(self) -> None:
        if self.offline_path.exists():
            payload = json.loads(self.offline_path.read_text())
            self.user_features = payload.get("users", {})
            self.item_features = payload.get("items", {})
        if self.item_metadata_path.exists():
            item_payload = json.loads(self.item_metadata_path.read_text())
            for item_id, features in item_payload.items():
                self.item_features.setdefault(item_id, {}).update(features)

    def get_user_features(self, user_id: str) -> dict:
        return self.user_features.get(user_id, {"engagement_score": 0.0, "preferred_categories": []})

    def get_item_features(self, item_id: str) -> dict:
        return self.item_features.get(item_id, {"category": "unknown", "popularity": 0.0, "price_tier": 1})

    def join_features(self, user_id: str, item_id: str, context: dict) -> dict:
        user = self.get_user_features(user_id)
        item = self.get_item_features(item_id)
        preferred = user.get("preferred_categories", [])
        category_match = float(item.get("category") in preferred)
        hour_of_day = context.get("hour_of_day", 12)
        device_type = context.get("device_type", "web")
        device_score = 1.0 if device_type == "ios" else 0.75 if device_type == "android" else 0.5
        evening_score = 1.0 if 18 <= hour_of_day <= 23 else 0.3
        return {
            "engagement_score": float(user.get("engagement_score", 0.0)),
            "category_match": category_match,
            "popularity": float(item.get("popularity", 0.0)),
            "price_tier": float(item.get("price_tier", 1)),
            "device_score": device_score,
            "evening_score": evening_score,
        }

    @staticmethod
    def as_vector(features: dict) -> np.ndarray:
        return np.array([
            features["engagement_score"],
            features["category_match"],
            features["popularity"],
            features["price_tier"],
            features["device_score"],
            features["evening_score"],
        ], dtype=np.float32)
