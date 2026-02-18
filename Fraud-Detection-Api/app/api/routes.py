"""
Fraud Detection API routes.
POST /predict       — single transaction scoring
POST /predict/batch — batch scoring
GET  /health        — health check
GET  /model/info    — model metadata
GET  /drift/status  — drift monitoring status
POST /drift/check   — trigger manual drift check
POST /cache/flush   — flush prediction cache
"""

import time
from fastapi import APIRouter, Request, HTTPException

from app.api.schemas import (
    TransactionRequest,
    PredictionResponse,
    BatchRequest,
    BatchResponse,
    HealthResponse,
    ModelInfoResponse,
    DriftStatusResponse,
    ErrorResponse,
)
from app.services.inference import model_service
from app.services.cache import cache_service
from app.middleware.circuit_breaker import circuit_breaker, CircuitState
from app.middleware.rate_limit import rate_limiter
from app.monitoring.drift import drift_monitor
from app.monitoring.metrics import (
    PREDICTION_COUNT,
    PREDICTION_LATENCY,
    PREDICTION_SCORE,
    CACHE_HITS,
    CACHE_MISSES,
    CIRCUIT_STATE,
    DRIFT_PSI,
    DRIFT_ALERT,
    RATE_LIMITED,
)
from app.config import settings

router = APIRouter()
_start_time = time.time()


@router.post(
    "/predict",
    response_model=PredictionResponse,
    responses={429: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
    summary="Score a single transaction for fraud",
    tags=["Prediction"],
)
async def predict(txn: TransactionRequest, request: Request):
    # Rate limiting
    if not rate_limiter.check(request):
        RATE_LIMITED.inc()
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again shortly.",
        )

    # Circuit breaker
    if not circuit_breaker.is_call_allowed:
        CIRCUIT_STATE.set(1)
        raise HTTPException(
            status_code=503,
            detail=f"Service temporarily unavailable (circuit breaker {circuit_breaker.state.value})",
        )

    # Check cache
    cached_result = cache_service.get_prediction(txn.features)
    if cached_result:
        CACHE_HITS.inc()
        return PredictionResponse(
            transaction_id=txn.transaction_id,
            cached=True,
            **cached_result,
        )
    CACHE_MISSES.inc()

    # Inference
    try:
        result = model_service.predict(txn.features)
        circuit_breaker.record_success()

        # Update metrics
        label = "fraud" if result["is_fraud"] else "legit"
        PREDICTION_COUNT.labels(result=label).inc()
        PREDICTION_LATENCY.observe(result["latency_ms"] / 1000)
        PREDICTION_SCORE.observe(result["fraud_score"])
        _update_circuit_gauge()

        # Cache result
        cache_service.set_prediction(txn.features, {
            "fraud_score": result["fraud_score"],
            "is_fraud": result["is_fraud"],
            "threshold": result["threshold"],
            "latency_ms": result["latency_ms"],
        })

        # Record for drift monitoring
        drift_monitor.record_prediction(result["fraud_score"], result["is_fraud"])

        return PredictionResponse(
            transaction_id=txn.transaction_id,
            fraud_score=result["fraud_score"],
            is_fraud=result["is_fraud"],
            threshold=result["threshold"],
            latency_ms=result["latency_ms"],
            cached=False,
        )

    except Exception as e:
        circuit_breaker.record_failure()
        _update_circuit_gauge()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post(
    "/predict/batch",
    response_model=BatchResponse,
    summary="Score a batch of transactions",
    tags=["Prediction"],
)
async def predict_batch(batch: BatchRequest, request: Request):
    if not rate_limiter.check(request):
        RATE_LIMITED.inc()
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")

    if not circuit_breaker.is_call_allowed:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable.")

    start = time.time()

    try:
        features_list = [txn.features for txn in batch.transactions]
        raw_results = model_service.predict_batch(features_list)
        circuit_breaker.record_success()

        total_ms = round((time.time() - start) * 1000, 2)

        results = []
        for i, (txn, raw) in enumerate(zip(batch.transactions, raw_results)):
            results.append(PredictionResponse(
                transaction_id=txn.transaction_id,
                fraud_score=raw["fraud_score"],
                is_fraud=raw["is_fraud"],
                threshold=raw["threshold"],
                latency_ms=round(total_ms / len(batch.transactions), 2),
                cached=False,
            ))

            # Metrics + drift
            label = "fraud" if raw["is_fraud"] else "legit"
            PREDICTION_COUNT.labels(result=label).inc()
            PREDICTION_SCORE.observe(raw["fraud_score"])
            drift_monitor.record_prediction(raw["fraud_score"], raw["is_fraud"])

        PREDICTION_LATENCY.observe(total_ms / 1000)

        return BatchResponse(results=results, total_latency_ms=total_ms, count=len(results))

    except Exception as e:
        circuit_breaker.record_failure()
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["Operations"],
)
async def health():
    return HealthResponse(
        status="healthy" if model_service.is_loaded else "degraded",
        model_loaded=model_service.is_loaded,
        cache_available=cache_service.is_available,
        circuit_breaker=circuit_breaker.state.value,
        uptime_seconds=round(time.time() - _start_time, 1),
        version=settings.app_version,
    )


@router.get(
    "/model/info",
    response_model=ModelInfoResponse,
    summary="Model metadata and training metrics",
    tags=["Operations"],
)
async def model_info():
    return model_service.get_info()


@router.get(
    "/drift/status",
    response_model=DriftStatusResponse,
    summary="Data drift monitoring status",
    tags=["Monitoring"],
)
async def drift_status():
    return drift_monitor.get_status()


@router.post(
    "/drift/check",
    summary="Trigger manual drift check",
    tags=["Monitoring"],
)
async def drift_check():
    report = drift_monitor.check_drift()
    if report:
        DRIFT_PSI.set(report["psi"])
        DRIFT_ALERT.set(1 if report["drift_detected"] else 0)
        return report
    return {"message": "Not enough data in window for drift check", "status": drift_monitor.get_status()}


@router.post(
    "/cache/flush",
    summary="Flush prediction cache",
    tags=["Operations"],
)
async def cache_flush():
    deleted = cache_service.flush()
    return {"flushed": deleted}


def _update_circuit_gauge():
    state = circuit_breaker.state
    if state == CircuitState.CLOSED:
        CIRCUIT_STATE.set(0)
    elif state == CircuitState.OPEN:
        CIRCUIT_STATE.set(1)
    else:
        CIRCUIT_STATE.set(2)
