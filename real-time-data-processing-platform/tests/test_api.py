from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

import rtdp.api as api_module
from rtdp.config import Settings
from rtdp.service import RealtimeProcessingService


def test_api_ingest_and_status(tmp_path: Path):
    api_module.service = RealtimeProcessingService(Settings(db_path=tmp_path / "api.db"))
    with TestClient(api_module.app) as client:
        payload = {
            "event_id": "evt_api_1",
            "entity_id": "acct_api_1",
            "event_type": "purchase",
            "occurred_at": "2026-04-01T12:00:00Z",
            "payload": {"amount": 18},
            "idempotency_key": "acct_api_1-evt_api_1",
            "failure_mode": "none",
        }
        response = client.post("/v1/events", json=payload)
        assert response.status_code == 200
        assert response.json()["accepted"] == 1
        status = client.get("/v1/status")
        assert status.status_code == 200
        assert "metrics" in status.json()
