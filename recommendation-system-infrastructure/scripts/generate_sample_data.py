from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

fake = Faker()
rng = np.random.default_rng(13)


CATEGORIES = ["sports", "beauty", "tech", "fashion", "home", "books", "fitness", "food"]
DEVICES = ["web", "ios", "android"]


def main() -> None:
    data_raw = Path("data/raw")
    data_processed = Path("data/processed")
    artifacts = Path("artifacts/models")
    mlruns = Path("artifacts/mlruns")
    benchmarks = Path("artifacts/benchmarks")
    logs = Path("logs")
    for path in [data_raw, data_processed, artifacts, mlruns, benchmarks, logs]:
        path.mkdir(parents=True, exist_ok=True)

    users = []
    for idx in range(250):
        preferred = rng.choice(CATEGORIES, size=2, replace=False).tolist()
        users.append({
            "user_id": f"user_{idx:04d}",
            "age_bucket": rng.choice(["18-24", "25-34", "35-44", "45+"]),
            "preferred_categories": preferred,
            "engagement_score": round(float(rng.uniform(0.2, 1.0)), 3),
        })
    users_df = pd.DataFrame(users)
    users_df.to_csv(data_raw / "users.csv", index=False)

    items = []
    for idx in range(1000):
        category = rng.choice(CATEGORIES)
        items.append({
            "item_id": f"item_{idx:04d}",
            "title": f"{category.title()} {fake.word().title()} {idx}",
            "category": category,
            "popularity": round(float(rng.uniform(0.1, 1.0)), 3),
            "price_tier": int(rng.integers(1, 5)),
        })
    items_df = pd.DataFrame(items)
    items_df.to_csv(data_raw / "items.csv", index=False)

    interactions = []
    for _ in range(12000):
        user = users_df.sample(1, random_state=int(rng.integers(0, 1_000_000))).iloc[0]
        preferred = set(user.preferred_categories)
        category = rng.choice(list(preferred) + CATEGORIES, p=None)
        candidate_pool = items_df[items_df.category == category]
        if candidate_pool.empty:
            candidate_pool = items_df
        item = candidate_pool.sample(1, random_state=int(rng.integers(0, 1_000_000))).iloc[0]
        clicked = int(rng.random() < (0.55 if item.category in preferred else 0.18))
        purchased = int(clicked and rng.random() < (0.12 + item.popularity * 0.12))
        interactions.append({
            "user_id": user.user_id,
            "item_id": item.item_id,
            "surface": rng.choice(["home", "search", "related_items"]),
            "clicked": clicked,
            "purchased": purchased,
            "seconds_watched": int(rng.integers(5, 240)),
            "position": int(rng.integers(1, 21)),
            "hour_of_day": int(rng.integers(0, 24)),
            "device_type": rng.choice(DEVICES),
        })
    interactions_df = pd.DataFrame(interactions)
    interactions_df.to_csv(data_raw / "interactions.csv", index=False)

    offline_features = {
        "users": {row.user_id: {"preferred_categories": row.preferred_categories, "engagement_score": row.engagement_score} for row in users_df.itertuples(index=False)},
        "items": {row.item_id: {"category": row.category, "popularity": row.popularity, "price_tier": row.price_tier} for row in items_df.itertuples(index=False)},
    }
    (data_processed / "offline_features.json").write_text(json.dumps(offline_features, indent=2))
    item_features = {row.item_id: {"title": row.title, "category": row.category, "popularity": row.popularity, "price_tier": row.price_tier} for row in items_df.itertuples(index=False)}
    (data_processed / "item_features.json").write_text(json.dumps(item_features, indent=2))


if __name__ == "__main__":
    main()
