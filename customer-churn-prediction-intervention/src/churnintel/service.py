from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from xgboost import XGBClassifier

from churnintel.config import settings
from churnintel.features import align_model_frame, build_feature_table, model_input_frame
from churnintel.interventions import choose_intervention
from churnintel.schemas import AccountPayload, Driver, ExplanationResponse, PredictionResponse


@dataclass(slots=True)
class ModelService:
    artifact_dir: Path
    ready: bool
    model: XGBClassifier | None = None
    metadata: dict | None = None
    explanations: dict | None = None
    queue_df: pd.DataFrame | None = None

    @classmethod
    def from_artifacts(cls, artifact_dir: Path | None = None) -> "ModelService":
        artifact_dir = artifact_dir or settings.artifact_dir
        required = [
            artifact_dir / "model.json",
            artifact_dir / "metadata.json",
            artifact_dir / "account_explanations.json",
            artifact_dir / "top_risk_accounts.csv",
        ]
        if not all(path.exists() for path in required):
            return cls(artifact_dir=artifact_dir, ready=False)

        metadata = json.loads((artifact_dir / "metadata.json").read_text())
        explanations = json.loads((artifact_dir / "account_explanations.json").read_text())
        queue_df = pd.read_csv(artifact_dir / "top_risk_accounts.csv")

        model = XGBClassifier()
        model.load_model(artifact_dir / "model.json")
        return cls(
            artifact_dir=artifact_dir,
            ready=True,
            model=model,
            metadata=metadata,
            explanations=explanations,
            queue_df=queue_df,
        )

    def predict(self, payload: AccountPayload) -> PredictionResponse:
        raw_df = pd.DataFrame([payload.model_dump()])
        raw_df["churned_60d"] = 0
        feature_df = build_feature_table(raw_df)
        model_frame = model_input_frame(feature_df)
        aligned = align_model_frame(model_frame, self.metadata["feature_columns"])
        probability = float(self.model.predict_proba(aligned)[:, 1][0])

        decision = choose_intervention(
            score=probability,
            monthly_recurring_revenue=float(payload.monthly_recurring_revenue),
            unresolved_tickets=int(payload.unresolved_tickets),
            payment_failures_90d=int(payload.payment_failures_90d),
            feature_adoption_score=float(payload.feature_adoption_score),
            plan_tier=str(payload.plan_tier),
        )

        explanation = self._compute_inline_explanation(feature_df)
        return PredictionResponse(
            account_id=payload.account_id,
            churn_probability=round(probability, 4),
            risk_tier=decision.risk_tier,
            recommended_action=decision.recommended_action,
            priority=decision.priority,
            owner=decision.owner,
            rationale=decision.rationale,
            top_drivers=explanation,
        )

    def _compute_inline_explanation(self, feature_df: pd.DataFrame) -> list[Driver]:
        row = feature_df.iloc[0]
        candidates = [
            ("days_since_last_activity", float(row["days_since_last_activity"]), "raises"),
            ("engagement_delta", float(abs(row["engagement_delta"])), "raises" if row["engagement_delta"] < 0 else "reduces"),
            ("unresolved_tickets", float(row["unresolved_tickets"]), "raises"),
            ("payment_failures_90d", float(row["payment_failures_90d"]), "raises"),
            ("feature_adoption_score", float(abs(0.6 - row["feature_adoption_score"])), "raises" if row["feature_adoption_score"] < 0.6 else "reduces"),
            ("nps_score", float(abs(min(row["nps_score"], 0))), "raises" if row["nps_score"] < 0 else "reduces"),
        ]
        candidates.sort(key=lambda item: abs(item[1]), reverse=True)

        drivers = []
        for feature_name, impact, direction in candidates[:5]:
            feature_value = float(row[feature_name]) if feature_name in row else float(impact)
            drivers.append(
                Driver(
                    feature=feature_name,
                    display_name=feature_name.replace("_", " "),
                    feature_value=round(feature_value, 4),
                    impact=round(float(impact), 5),
                    direction=direction,
                )
            )
        return drivers

    def top_risk_accounts(self, limit: int = 25, plan_tier: str | None = None) -> list[dict]:
        df = self.queue_df.copy()
        if plan_tier:
            df = df[df["plan_tier"].str.lower() == plan_tier.lower()]
        return df.head(limit).to_dict(orient="records")

    def intervention_queue(self, limit: int = 25) -> list[dict]:
        columns = [
            "account_id",
            "plan_tier",
            "industry",
            "monthly_recurring_revenue",
            "churn_probability",
            "risk_tier",
            "recommended_action",
            "priority",
            "owner",
        ]
        return self.queue_df[columns].head(limit).to_dict(orient="records")

    def explain(self, account_id: str) -> ExplanationResponse | None:
        payload = self.explanations.get(account_id)
        if payload is None:
            return None
        return ExplanationResponse(**payload)
