from fastapi.testclient import TestClient
from gateway_service.main import app
import gateway_service.main as gateway_module


class DummyAsyncClient:
    def __init__(self, responses):
        self.responses = responses

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url):
        class Response:
            def __init__(self, payload):
                self._payload = payload
            def raise_for_status(self):
                return None
            def json(self):
                return self._payload
        if url.endswith("/products"):
            return Response({"products": [{"sku": "sku-101"}]})
        return Response({"status": "ok"})

    async def post(self, url, json):
        class Response:
            def raise_for_status(self):
                return None
            def json(self):
                return {"order": {"sku": json["sku"], "quantity": json["quantity"]}}
        return Response()


def test_gateway_products(monkeypatch):
    monkeypatch.setattr(gateway_module.httpx, "AsyncClient", lambda timeout=5.0: DummyAsyncClient({}))
    client = TestClient(app)
    response = client.get("/products")
    assert response.status_code == 200
    assert response.json()["products"][0]["sku"] == "sku-101"


def test_gateway_health(monkeypatch):
    monkeypatch.setattr(gateway_module.httpx, "AsyncClient", lambda timeout=5.0: DummyAsyncClient({}))
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
