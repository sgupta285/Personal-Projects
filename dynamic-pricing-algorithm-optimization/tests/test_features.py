import pandas as pd

from pricing_engine.features import build_feature_table


def test_feature_table_builds_pricing_columns():
    raw = pd.DataFrame(
        [
            {
                "date": "2026-01-01",
                "product_id": "sku-001",
                "category": "electronics",
                "channel": "web",
                "base_price": 100.0,
                "unit_cost": 60.0,
                "price": 95.0,
                "discount_pct": 0.05,
                "competitor_price": 97.0,
                "inventory_level": 80,
                "max_inventory": 100,
                "seasonality_index": 1.0,
                "demand_regime": "normal",
                "returning_customer_share": 0.4,
                "page_views": 120,
                "cart_add_rate": 0.15,
                "is_holiday": 0,
                "weekday": 3,
                "month": 1,
                "units_sold": 10,
            },
            {
                "date": "2026-01-02",
                "product_id": "sku-001",
                "category": "electronics",
                "channel": "web",
                "base_price": 100.0,
                "unit_cost": 60.0,
                "price": 94.0,
                "discount_pct": 0.06,
                "competitor_price": 96.0,
                "inventory_level": 75,
                "max_inventory": 100,
                "seasonality_index": 1.0,
                "demand_regime": "normal",
                "returning_customer_share": 0.42,
                "page_views": 130,
                "cart_add_rate": 0.16,
                "is_holiday": 0,
                "weekday": 4,
                "month": 1,
                "units_sold": 12,
            },
        ]
    )
    features = build_feature_table(raw)
    assert "inventory_pressure" in features.columns
    assert "competitor_gap_pct" in features.columns
    assert "units_sold_lag_1" in features.columns
