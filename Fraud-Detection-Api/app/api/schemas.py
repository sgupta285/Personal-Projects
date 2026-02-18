from pydantic import BaseModel, Field


class TransactionRequest(BaseModel):
    """Single transaction for fraud scoring."""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    features: list[float] = Field(
        ...,
        description="Feature vector (30 features: Time, V1-V28, Amount)",
        min_length=30,
        max_length=30,
    )

    model_config = {"json_schema_extra": {
        "examples": [{
            "transaction_id": "txn_001",
            "features": [0.0] * 30,
        }]
    }}


class PredictionResponse(BaseModel):
    transaction_id: str
    fraud_score: float = Field(..., ge=0.0, le=1.0)
    is_fraud: bool
    threshold: float
    latency_ms: float
    cached: bool = False


class BatchRequest(BaseModel):
    transactions: list[TransactionRequest] = Field(..., max_length=100)


class BatchResponse(BaseModel):
    results: list[PredictionResponse]
    total_latency_ms: float
    count: int


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    cache_available: bool
    circuit_breaker: str
    uptime_seconds: float
    version: str


class ModelInfoResponse(BaseModel):
    loaded: bool
    model_type: str
    n_features: int
    feature_names: list[str]
    threshold: float
    training_metrics: dict


class DriftStatusResponse(BaseModel):
    total_predictions: int
    fraud_count: int
    fraud_rate_pct: float
    window_fill: int
    window_size: int
    alert_active: bool
    latest_psi: dict | None
    psi_history_length: int


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
