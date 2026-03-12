from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from xgboost import XGBRegressor

from pricing_engine.config import settings
from pricing_engine.optimizer import price_curve, recommend_for_row
from pricing_engine.schemas import PricingRequest, PricingResponse


@dataclass(slots=True)
class PricingService:
    artifact_dir: Path
    ready: bool
    model: XGBRegressor | None = None
    metadata: dict | None = None
    recommendations: pd.DataFrame | None = None
    backtest_summary: dict | None = None
    sample_curve: pd.DataFrame | None = None

    @classmethod
    def from_artifacts(cls, artifact_dir: Path | None = None) -> "PricingService":
        artifact_dir = artifact_dir or settings.artifact_dir
        required = [
            artifact_dir / "model.json",
            artifact_dir / "metadata.json",
            artifact_dir / "top_recommendations.csv",
            artifact_dir / "backtest_summary.json",
            artifact_dir / "sample_price_curve.csv",
        ]
        if not all(path.exists() for path in required):
            return cls(artifact_dir=artifact_dir, ready=False)

        model = XGBRegressor()
        model.load_model(artifact_dir / "model.json")
        metadata = json.loads((artifact_dir / "metadata.json").read_text())
        recommendations = pd.read_csv(artifact_dir / "top_recommendations.csv")
        backtest_summary = json.loads((artifact_dir / "backtest_summary.json").read_text())
        sample_curve = pd.read_csv(artifact_dir / "sample_price_curve.csv")
        return cls(
            artifact_dir=artifact_dir,
            ready=True,
            model=model,
            metadata=metadata,
            recommendations=recommendations,
            backtest_summary=backtest_summary,
            sample_curve=sample_curve,
        )

    def recommend(self, payload: PricingRequest) -> PricingResponse:
        row = pd.Series(payload.model_dump())
        recommendation = recommend_for_row(row, self.model, self.metadata)
        return PricingResponse(**recommendation.__dict__)

    def top_recommendations(self, limit: int = 25) -> list[dict]:
        return self.recommendations.head(limit).to_dict(orient="records")

    def sample_sensitivity(self) -> dict:
        return {
            "curve": self.sample_curve.to_dict(orient="records"),
            "recommended_peak_profit": float(self.sample_curve["expected_profit"].max()),
        }
