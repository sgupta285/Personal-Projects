from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class PipelineConfig:
    raw: dict[str, Any]

    @property
    def dataset_path(self) -> Path:
        return Path(self.raw["dataset"]["path"])

    @property
    def target_column(self) -> str:
        return self.raw["dataset"]["target_column"]

    @property
    def train_size(self) -> float:
        return float(self.raw["dataset"]["train_size"])

    @property
    def random_state(self) -> int:
        return int(self.raw["dataset"]["random_state"])

    @property
    def id_columns(self) -> list[str]:
        return list(self.raw["dataset"].get("id_columns", []))


def load_config(path: str | Path = "configs/pipeline.yaml") -> PipelineConfig:
    with open(path, "r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    return PipelineConfig(raw=raw)
