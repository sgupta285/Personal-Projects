from fastapi.testclient import TestClient

from app.main import app


def test_live_endpoint():
    with TestClient(app) as client:
        response = client.get("/health/live")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_prediction_with_features():
    with TestClient(app) as client:
        response = client.post(
            "/v1/predict",
            json={
                "request_id": "test-1",
                "features": {
                    "account_tenure_days": 50,
                    "avg_session_seconds": 300,
                    "prior_purchases": 2,
                    "cart_additions_7d": 4,
                    "email_click_rate": 0.2,
                    "discount_sensitivity": 0.4,
                    "inventory_score": 0.7,
                    "device_trust_score": 0.8
                }
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["request_id"] == "test-1"
        assert body["prediction_label"] in {"low_risk", "high_intent"}
