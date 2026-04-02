import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


if __name__ == "__main__":
    client = TestClient(app)
    response = client.get("/usage/summary")
    response.raise_for_status()
    payload = response.json()
    print(json.dumps({"totals": payload["totals"], "points": len(payload["time_series"])}, indent=2))
