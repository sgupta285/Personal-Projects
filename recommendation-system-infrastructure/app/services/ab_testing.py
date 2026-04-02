from __future__ import annotations

import hashlib


class ExperimentService:
    def __init__(self, experiment_name: str = "ranking_strategy_v1") -> None:
        self.experiment_name = experiment_name
        self.variants = ("baseline", "neural_rerank")

    def get_assignment(self, user_id: str) -> dict[str, str]:
        digest = hashlib.sha256(user_id.encode("utf-8")).hexdigest()
        bucket = int(digest[:8], 16) % 100
        variant = self.variants[0] if bucket < 50 else self.variants[1]
        return {"experiment_name": self.experiment_name, "variant": variant}

    def summary(self, events) -> dict:
        rows = {}
        for event in events:
            row = rows.setdefault(event.variant, {"users": 0, "clicks": 0, "conversions": 0})
            row["users"] += 1
            row["clicks"] += event.clicked
            row["conversions"] += event.converted
        for variant, row in rows.items():
            row["ctr"] = row["clicks"] / row["users"] if row["users"] else 0.0
            row["conversion_rate"] = row["conversions"] / row["users"] if row["users"] else 0.0
        return {"experiment_name": self.experiment_name, "variants": rows}
