"""
Model inference service — loads trained model + scaler and provides predictions.
"""

import os
import json
import time
import numpy as np
import joblib
import structlog

from app.config import settings

logger = structlog.get_logger()


class FraudModelService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.metadata: dict = {}
        self.feature_names: list[str] = []
        self.threshold: float = settings.model_threshold
        self._loaded = False

    def load(self) -> bool:
        """Load model artifacts from disk."""
        model_path = settings.model_path
        scaler_path = model_path.replace("fraud_model.joblib", "scaler.joblib")
        metadata_path = model_path.replace("fraud_model.joblib", "model_metadata.json")

        if not os.path.exists(model_path):
            logger.warning("model_not_found", path=model_path)
            return False

        try:
            start = time.time()
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)

            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    self.metadata = json.load(f)
                self.feature_names = self.metadata.get("feature_names", [])
                self.threshold = self.metadata.get("threshold", self.threshold)

            load_time = time.time() - start
            self._loaded = True
            logger.info(
                "model_loaded",
                path=model_path,
                load_time_ms=round(load_time * 1000, 1),
                n_features=len(self.feature_names),
            )
            return True
        except Exception as e:
            logger.error("model_load_error", error=str(e))
            return False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def predict(self, features: list[float]) -> dict:
        """
        Run fraud prediction on a single transaction.
        Returns: { score, is_fraud, latency_ms, features_used }
        """
        if not self._loaded:
            raise RuntimeError("Model not loaded")

        start = time.time()

        feature_array = np.array(features).reshape(1, -1)

        # Scale features
        if self.scaler is not None:
            feature_array = self.scaler.transform(feature_array)

        # Get probability
        proba = self.model.predict_proba(feature_array)[0]
        fraud_score = float(proba[1])
        is_fraud = fraud_score >= self.threshold

        latency_ms = round((time.time() - start) * 1000, 2)

        return {
            "fraud_score": round(fraud_score, 6),
            "is_fraud": is_fraud,
            "threshold": self.threshold,
            "latency_ms": latency_ms,
            "features_used": len(features),
        }

    def predict_batch(self, batch: list[list[float]]) -> list[dict]:
        """Run fraud prediction on a batch of transactions."""
        if not self._loaded:
            raise RuntimeError("Model not loaded")

        start = time.time()

        feature_array = np.array(batch)
        if self.scaler is not None:
            feature_array = self.scaler.transform(feature_array)

        probas = self.model.predict_proba(feature_array)
        total_latency_ms = round((time.time() - start) * 1000, 2)
        per_item_latency = round(total_latency_ms / len(batch), 2)

        results = []
        for i, proba in enumerate(probas):
            fraud_score = float(proba[1])
            results.append({
                "index": i,
                "fraud_score": round(fraud_score, 6),
                "is_fraud": fraud_score >= self.threshold,
                "threshold": self.threshold,
            })

        return results

    def get_info(self) -> dict:
        return {
            "loaded": self._loaded,
            "model_type": self.metadata.get("model_type", "unknown"),
            "n_features": len(self.feature_names),
            "feature_names": self.feature_names,
            "threshold": self.threshold,
            "training_metrics": {
                "precision": self.metadata.get("precision"),
                "recall": self.metadata.get("recall"),
                "f1_score": self.metadata.get("f1_score"),
                "auc_roc": self.metadata.get("auc_roc"),
            },
        }


# Singleton instance
model_service = FraudModelService()
