from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from torch import nn

from app.services.feature_store import FeatureStore


class Ranker(nn.Module):
    def __init__(self, input_dim: int = 6) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
        )

    def forward(self, x):
        return self.network(x)


class RankingService:
    def __init__(self, feature_store: FeatureStore) -> None:
        self.feature_store = feature_store
        self.model = Ranker()

    def load(self, model_path: str) -> None:
        path = Path(model_path)
        if path.exists():
            state = torch.load(path, map_location="cpu")
            self.model.load_state_dict(state)
        self.model.eval()

    def rerank(self, user_id: str, candidates: list[tuple[str, float]], context: dict, variant: str) -> list[dict]:
        rows = []
        for item_id, candidate_score in candidates:
            features = self.feature_store.join_features(user_id, item_id, context)
            vector = torch.tensor(self.feature_store.as_vector(features), dtype=torch.float32)
            neural_score = float(self.model(vector).item())
            score = candidate_score if variant == "baseline" else 0.55 * candidate_score + 0.45 * neural_score
            rows.append({
                "item_id": item_id,
                "score": score,
                "candidate_score": float(candidate_score),
                "neural_score": neural_score,
                "features": features,
            })
        rows.sort(key=lambda row: row["score"], reverse=True)
        return rows
