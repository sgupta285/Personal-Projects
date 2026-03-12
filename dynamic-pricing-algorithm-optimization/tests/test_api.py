from fastapi.testclient import TestClient

from api.main import app


class FakeService:
    ready = True
    artifact_dir = "."

    def recommend(self, payload):
        return {
            "product_id": payload.product_id,
            "current_price": payload.price,
            "recommended_price": payload.price + 4,
            "price_change_pct": 4.0,
            "expected_profit_current": 100.0,
            "expected_profit_recommended": 118.0,
            "expected_profit_uplift_pct": 18.0,
            "expected_units_current": 10.0,
            "expected_units_recommended": 9.6,
            "expected_revenue_current": 250.0,
            "expected_revenue_recommended": 278.4,
            "guardrails": {"min_price": 20.0, "max_price": 40.0},
            "explanation": ["Inventory is tight."],
        }

    def top_recommendations(self, limit=25):
        return [{"product_id": "sku-001", "recommended_price": 42.0}]

    backtest_summary = {"profit_uplift_pct": 5.5}
    sample_curve = __import__("pandas").DataFrame([{"candidate_price": 20, "expected_profit": 10, "expected_revenue": 30}])


def test_recommend_endpoint(monkeypatch):
    monkeypatch.setattr("api.main.service", FakeService())
    client = TestClient(app)
    payload = {
        "date": "2026-02-01",
        "product_id": "sku-001",
        "category": "electronics",
        "channel": "web",
        "demand_regime": "normal",
        "base_price": 100.0,
        "unit_cost": 60.0,
        "price": 95.0,
        "discount_pct": 0.05,
        "promotion_intensity": 0.05,
        "competitor_price": 96.0,
        "competitor_gap_pct": -0.01,
        "inventory_level": 80,
        "max_inventory": 100,
        "inventory_pressure": 0.2,
        "seasonality_index": 1.0,
        "returning_customer_share": 0.4,
        "page_views": 100,
        "cart_add_rate": 0.15,
        "conversion_proxy": 15.0,
        "weekday": 1,
        "month": 2,
        "is_weekend": 0,
        "is_holiday": 0,
        "price_index_vs_base": 0.95,
        "gross_margin_per_unit": 35.0,
        "markdown_flag": 0,
        "units_sold_lag_1": 10.0,
        "units_sold_lag_7": 9.0,
        "units_sold_rolling_7": 11.0,
        "price_lag_1": 96.0,
        "price_change_pct": -0.01,
    }
    response = client.post("/recommend-price", json=payload)
    assert response.status_code == 200
    assert response.json()["recommended_price"] == 99.0
