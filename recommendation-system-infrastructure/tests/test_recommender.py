from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.runtime import runtime


def setup_module():
    if not Path("artifacts/models/ranking_model.pt").exists():
        from scripts.generate_sample_data import main as seed_main
        from app.ml.train import train

        seed_main()
        train()
    runtime.load()


def test_home_recommendations():
    client = TestClient(app)
    response = client.post(
        "/v1/recommendations/home",
        json={
            "user_id": "user_0003",
            "surface": "home",
            "limit": 6,
            "context": {"hour_of_day": 21, "device_type": "ios"},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["surface"] == "home"
    assert len(body["items"]) == 6
    assert body["candidates_considered"] >= 50
