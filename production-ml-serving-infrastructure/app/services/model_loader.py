import json
from pathlib import Path
from typing import Any

import torch
from torch import nn

from app.core.config import settings
from app.schemas.prediction import FEATURE_ORDER, FeaturePayload


class ConversionModel(nn.Module):
    def __init__(self, input_size: int = 8):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


class ModelRepository:
    def __init__(self) -> None:
        self._model = None
        self._metadata = None

    def _load_metadata(self) -> dict[str, Any]:
        registry_path = settings.model_registry_path_obj
        if registry_path.exists():
            return json.loads(registry_path.read_text(encoding="utf-8"))
        return {
            "model_version": "untrained",
            "training_metrics": {},
            "feature_order": FEATURE_ORDER,
            "path": settings.model_path,
        }

    def _load_model(self) -> nn.Module | None:
        model_path = settings.model_path_obj
        if not model_path.exists():
            return None
        model = ConversionModel(input_size=len(FEATURE_ORDER))
        state = torch.load(model_path, map_location="cpu")
        model.load_state_dict(state)
        model.eval()
        return model

    def refresh(self) -> None:
        self._metadata = self._load_metadata()
        self._model = self._load_model()

    @property
    def metadata(self) -> dict[str, Any]:
        if self._metadata is None:
            self.refresh()
        return self._metadata

    @property
    def model(self) -> nn.Module | None:
        if self._model is None and settings.model_path_obj.exists():
            self.refresh()
        return self._model

    def is_ready(self) -> bool:
        return self.model is not None

    def predict_scores(self, payloads: list[FeaturePayload]) -> list[float]:
        if self.model is None:
            raise RuntimeError("Active model weights are not available.")
        matrix = torch.tensor([payload.to_vector() for payload in payloads], dtype=torch.float32)
        with torch.no_grad():
            logits = self.model(matrix).squeeze(-1)
            probs = torch.sigmoid(logits).cpu().numpy().tolist()
        return [float(item) for item in probs]
