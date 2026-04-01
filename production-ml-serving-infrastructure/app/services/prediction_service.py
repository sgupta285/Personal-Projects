import hashlib
import json
from time import perf_counter

from app.core.config import settings
from app.db.models import PredictionAuditLog
from app.db.session import get_session
from app.schemas.prediction import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    FeaturePayload,
    ModelInfoResponse,
    PredictionRequest,
    PredictionResponse,
)
from app.services.fallback import fallback_score
from app.services.metrics import FALLBACK_COUNTER, REQUEST_COUNTER, REQUEST_LATENCY


class PredictionService:
    def __init__(self, cache, model_repo, feature_store, batcher):
        self.cache = cache
        self.model_repo = model_repo
        self.feature_store = feature_store
        self.batcher = batcher

    async def predict(self, request: PredictionRequest) -> PredictionResponse:
        start = perf_counter()
        cache_key = self._build_cache_key(request)
        cached = await self.cache.get(cache_key)
        if cached is not None:
            cached_payload = dict(cached)
            cached_payload["cache_hit"] = True
            cached_payload["source"] = "cache"
            REQUEST_COUNTER.labels(endpoint="/v1/predict", status="cache_hit").inc()
            REQUEST_LATENCY.labels(endpoint="/v1/predict").observe(perf_counter() - start)
            return PredictionResponse(**cached_payload)

        features = self._resolve_features(request)
        used_fallback = False
        source = "live_model"
        if self.model_repo.is_ready():
            if settings.enable_dynamic_batching:
                score = await self.batcher.infer(features)
            else:
                score = self.model_repo.predict_scores([features])[0]
        elif settings.enable_fallback_model:
            score = fallback_score(features)
            source = "fallback_model"
            used_fallback = True
            FALLBACK_COUNTER.inc()
        else:
            raise RuntimeError("No active model is available and fallback is disabled.")

        response = PredictionResponse(
            request_id=request.request_id,
            prediction_label="high_intent" if score >= 0.5 else "low_risk",
            prediction_score=round(float(score), 6),
            cache_hit=False,
            source=source,
            model_version=self.model_repo.metadata.get("model_version", "unknown"),
            used_fallback=used_fallback,
        )
        await self.cache.set(cache_key, response.model_dump())
        self._write_audit_log(request, features, response)
        REQUEST_COUNTER.labels(endpoint="/v1/predict", status="success").inc()
        REQUEST_LATENCY.labels(endpoint="/v1/predict").observe(perf_counter() - start)
        return response

    async def predict_batch(self, batch_request: BatchPredictionRequest) -> BatchPredictionResponse:
        predictions = []
        for request in batch_request.requests:
            predictions.append(await self.predict(request))
        return BatchPredictionResponse(job_id=batch_request.job_id, predictions=predictions)

    async def clear_cache(self) -> dict:
        await self.cache.clear()
        return {"cleared": True}

    def model_info(self) -> ModelInfoResponse:
        metadata = self.model_repo.metadata
        return ModelInfoResponse(
            model_version=metadata.get("model_version", "unknown"),
            training_run_id=metadata.get("training_run_id"),
            training_metrics=metadata.get("training_metrics", {}),
            trained_at=metadata.get("trained_at"),
            feature_order=metadata.get("feature_order", []),
            path=metadata.get("path", settings.model_path),
        )

    def _build_cache_key(self, request: PredictionRequest) -> str:
        payload = {
            "customer_id": request.customer_id,
            "features": request.features.model_dump() if request.features else None,
        }
        raw = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _resolve_features(self, request: PredictionRequest) -> FeaturePayload:
        if request.features is not None:
            return request.features
        features = self.feature_store.get_customer_features(request.customer_id)
        if features is None:
            raise ValueError(f"Customer {request.customer_id} was not found in the online feature store.")
        return features

    def _write_audit_log(
        self,
        request: PredictionRequest,
        features: FeaturePayload,
        response: PredictionResponse,
    ) -> None:
        with get_session() as session:
            session.add(
                PredictionAuditLog(
                    request_id=request.request_id,
                    customer_id=request.customer_id,
                    prediction_label=response.prediction_label,
                    prediction_score=response.prediction_score,
                    source=response.source,
                    used_fallback=1 if response.used_fallback else 0,
                    feature_payload=features.model_dump(),
                )
            )
            session.commit()
