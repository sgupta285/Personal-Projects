import os
from pathlib import Path
from fastapi.testclient import TestClient

os.environ["ORDER_DB_PATH"] = "/tmp/test-orders-platform.db"

from orders_service.main import app, init_db  # noqa: E402


def test_create_order():
    db_path = Path("/tmp/test-orders-platform.db")
    if db_path.exists():
        db_path.unlink()
    init_db()

    client = TestClient(app)
    response = client.post("/orders", json={"customer_id": "u1", "sku": "sku-101", "quantity": 1})
    assert response.status_code == 200
    payload = response.json()["order"]
    assert payload["sku"] == "sku-101"

    listing = client.get("/orders")
    assert listing.status_code == 200
    assert len(listing.json()["orders"]) >= 1
