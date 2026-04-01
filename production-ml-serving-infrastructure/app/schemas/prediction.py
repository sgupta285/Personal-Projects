from typing import Literal

from pydantic import BaseModel, Field, model_validator


FEATURE_ORDER = [
    "account_tenure_days",
    "avg_session_seconds",
    "prior_purchases",
    "cart_additions_7d",
    "email_click_rate",
    "discount_sensitivity",
    "inventory_score",
    "device_trust_score",
]


class FeaturePayload(BaseModel):
    account_tenure_days: float
    avg_session_seconds: float
    prior_purchases: float
    cart_additions_7d: float
    email_click_rate: float
    discount_sensitivity: float
    inventory_score: float
    device_trust_score: float

    def to_vector(self) -> list[float]:
        return [float(getattr(self, name)) for name in FEATURE_ORDER]


class PredictionRequest(BaseModel):
    request_id: str = Field(min_length=2)
    customer_id: str | None = None
    features: FeaturePayload | None = None

    @model_validator(mode="after")
    def validate_payload(self):
        if self.customer_id is None and self.features is None:
            raise ValueError("Either customer_id or features must be provided.")
        return self


class PredictionResponse(BaseModel):
    request_id: str
    prediction_label: Literal["low_risk", "high_intent"]
    prediction_score: float
    cache_hit: bool = False
    source: Literal["live_model", "fallback_model", "cache"]
    model_version: str
    used_fallback: bool = False


class BatchPredictionRequest(BaseModel):
    job_id: str
    requests: list[PredictionRequest]


class BatchPredictionResponse(BaseModel):
    job_id: str
    predictions: list[PredictionResponse]


class ModelInfoResponse(BaseModel):
    model_version: str
    training_run_id: str | None = None
    training_metrics: dict
    trained_at: str | None = None
    feature_order: list[str]
    path: str
