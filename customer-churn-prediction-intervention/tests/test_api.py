from fastapi.testclient import TestClient

from api.main import app


class FakeService:
    ready = True
    artifact_dir = "."

    def predict(self, payload):
        return {
            "account_id": payload.account_id,
            "churn_probability": 0.73,
            "risk_tier": "high",
            "recommended_action": "Lifecycle email with tailored value proof",
            "priority": "P1",
            "owner": "growth-marketing",
            "rationale": "Risk is elevated.",
            "top_drivers": [],
        }

    def top_risk_accounts(self, limit=25, plan_tier=None):
        return [{"account_id": "acct-1", "plan_tier": plan_tier or "growth"}]

    def intervention_queue(self, limit=25):
        return [{"account_id": "acct-1", "priority": "P1"}]

    def explain(self, account_id):
        return {
            "account_id": account_id,
            "churn_probability": 0.73,
            "risk_tier": "high",
            "recommended_action": "Lifecycle email with tailored value proof",
            "priority": "P1",
            "rationale": "Risk is elevated.",
            "drivers": [],
        }


def test_health_endpoint(monkeypatch):
    monkeypatch.setattr("api.main.service", FakeService())
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_predict_endpoint(monkeypatch):
    monkeypatch.setattr("api.main.service", FakeService())
    client = TestClient(app)
    payload = {
        "account_id": "acct-demo",
        "plan_tier": "growth",
        "contract_type": "monthly",
        "region": "North America",
        "industry": "SaaS",
        "monthly_recurring_revenue": 800,
        "seat_count": 15,
        "tenure_months": 8,
        "days_since_last_activity": 18,
        "avg_weekly_sessions_30d": 5.5,
        "avg_weekly_sessions_prev_30d": 8.4,
        "transactions_30d": 34,
        "transactions_prev_30d": 52,
        "support_tickets_90d": 3,
        "unresolved_tickets": 1,
        "payment_failures_90d": 0,
        "plan_change_count_180d": 1,
        "nps_score": 22,
        "csat_score": 3.9,
        "admin_logins_30d": 9,
        "api_calls_30d": 4200,
        "feature_adoption_score": 0.51,
        "onboarding_completion_pct": 0.68,
        "training_sessions_attended": 1,
        "auto_renew": False,
        "last_marketing_touch_days": 12,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert response.json()["risk_tier"] == "high"
