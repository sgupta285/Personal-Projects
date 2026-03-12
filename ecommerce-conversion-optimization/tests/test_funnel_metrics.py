import pandas as pd
from ecomopt.data_generation import expand_events


def test_expand_events_keeps_stage_order():
    sessions = pd.DataFrame([{
        "session_id": "sess-1",
        "user_id": "user-1",
        "started_at": "2026-03-01 10:00:00",
        "device_type": "mobile",
        "traffic_channel": "email",
        "product_category": "fashion",
        "user_recency": "active",
        "variant": "control",
        "landed": 1,
        "viewed_product": 1,
        "added_to_cart": 1,
        "started_checkout": 0,
        "purchased": 0,
        "order_value": 0.0,
    }])
    events = expand_events(sessions)
    assert list(events["stage_name"]) == ["landing", "product_page", "cart"]
    assert list(events["stage_order"]) == [1, 2, 3]
