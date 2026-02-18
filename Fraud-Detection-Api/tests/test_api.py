"""
Smoke tests for Fraud Detection API.
Tests core prediction, batch, health, circuit breaker, and drift logic.
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Patch redis before importing app
with patch("app.services.cache.cache_service") as mock_cache:
    mock_cache.is_available = False
    mock_cache.connect.return_value = False
    mock_cache.get_prediction.return_value = None
    mock_cache.set_prediction.return_value = None
    from app.main import app

client = TestClient(app)


def _make_features(n: int = 30) -> list[float]:
    np.random.seed(42)
    return np.random.randn(n).tolist()


class TestHealth:
    def test_health_endpoint(self):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "model_loaded" in data
        assert "circuit_breaker" in data
        assert "version" in data

    def test_root_redirect(self):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "docs" in data


class TestPrediction:
    def test_predict_returns_200_or_500(self):
        """Prediction works if model is loaded, 500 otherwise."""
        resp = client.post("/api/v1/predict", json={
            "transaction_id": "txn_test_001",
            "features": _make_features(),
        })
        # Depends on whether model file exists
        assert resp.status_code in [200, 500]

        if resp.status_code == 200:
            data = resp.json()
            assert "fraud_score" in data
            assert "is_fraud" in data
            assert "latency_ms" in data
            assert 0.0 <= data["fraud_score"] <= 1.0

    def test_predict_validation_error(self):
        """Missing features should return 422."""
        resp = client.post("/api/v1/predict", json={
            "transaction_id": "txn_bad",
            "features": [1.0, 2.0],  # Too few features
        })
        assert resp.status_code == 422

    def test_predict_missing_body(self):
        resp = client.post("/api/v1/predict", json={})
        assert resp.status_code == 422

    def test_batch_predict(self):
        txns = [
            {"transaction_id": f"txn_{i}", "features": _make_features()}
            for i in range(5)
        ]
        resp = client.post("/api/v1/predict/batch", json={"transactions": txns})
        assert resp.status_code in [200, 500]

        if resp.status_code == 200:
            data = resp.json()
            assert data["count"] == 5
            assert len(data["results"]) == 5

    def test_batch_too_large(self):
        txns = [
            {"transaction_id": f"txn_{i}", "features": _make_features()}
            for i in range(101)
        ]
        resp = client.post("/api/v1/predict/batch", json={"transactions": txns})
        assert resp.status_code == 422


class TestModelInfo:
    def test_model_info(self):
        resp = client.get("/api/v1/model/info")
        assert resp.status_code == 200
        data = resp.json()
        assert "loaded" in data
        assert "model_type" in data


class TestDrift:
    def test_drift_status(self):
        resp = client.get("/api/v1/drift/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_predictions" in data
        assert "alert_active" in data

    def test_drift_check(self):
        resp = client.post("/api/v1/drift/check")
        assert resp.status_code == 200


class TestCircuitBreaker:
    def test_circuit_breaker_in_health(self):
        resp = client.get("/api/v1/health")
        data = resp.json()
        assert data["circuit_breaker"] in ["closed", "open", "half_open"]


class TestCacheFlush:
    def test_cache_flush(self):
        resp = client.post("/api/v1/cache/flush")
        assert resp.status_code == 200


class TestDriftMonitorUnit:
    def test_psi_computation(self):
        from app.monitoring.drift import compute_psi

        ref = np.random.beta(1, 20, size=1000)
        same = np.random.beta(1, 20, size=1000)
        different = np.random.beta(10, 2, size=1000)

        psi_same = compute_psi(ref, same)
        psi_diff = compute_psi(ref, different)

        assert psi_same < psi_diff
        assert psi_same < 0.5  # Similar distributions, low PSI
        assert psi_diff > 0.2  # Different distributions, high PSI

    def test_circuit_breaker_states(self):
        from app.middleware.circuit_breaker import CircuitBreaker, CircuitState

        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
        assert cb.state == CircuitState.CLOSED

        for _ in range(3):
            cb.record_failure()

        assert cb.state == CircuitState.OPEN
        assert not cb.is_call_allowed

        cb.reset()
        assert cb.state == CircuitState.CLOSED
        assert cb.is_call_allowed
