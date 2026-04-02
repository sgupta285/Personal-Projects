from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.services.runtime import runtime

runtime.load()
client = TestClient(app)

response = client.post(
    "/v1/recommendations/home",
    json={
        "user_id": "user_0005",
        "surface": "home",
        "limit": 5,
        "context": {"hour_of_day": 19, "device_type": "ios"},
    },
)
response.raise_for_status()
body = response.json()
print({"items": len(body["items"]), "variant": body["variant"]})
