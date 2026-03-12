from fastapi.testclient import TestClient
from catalog_service.main import app


def test_catalog_products():
    client = TestClient(app)
    response = client.get("/products")
    assert response.status_code == 200
    body = response.json()
    assert len(body["products"]) >= 3
    assert body["products"][0]["sku"].startswith("sku-")
