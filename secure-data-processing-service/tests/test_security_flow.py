from __future__ import annotations

from pathlib import Path
import tempfile

import pytest
from fastapi.testclient import TestClient


def build_client(tmp_path: Path):
    import app.config as config
    config.settings.database_url = f"sqlite:///{tmp_path / 'service.db'}"
    config.settings.local_kms_key_path = tmp_path / 'kms.json'
    config.settings.local_secrets_file = tmp_path / 'secrets.json'
    config.settings.audit_log_path = tmp_path / 'audit.jsonl'
    from importlib import reload
    import app.database, app.main
    reload(app.database)
    reload(app.main)
    return TestClient(app.main.app)


def token_for(client: TestClient, username: str, password: str) -> str:
    code = client.get(f"/auth/mfa-demo/{username}").json()["demo_totp_code"]
    response = client.post("/auth/token", json={"username": username, "password": password, "mfa_code": code})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_create_and_read_record_with_redaction(tmp_path: Path):
    client = build_client(tmp_path)
    processor_token = token_for(client, "processor_north", "Processor123!")
    response = client.post(
        "/records",
        headers={"Authorization": f"Bearer {processor_token}"},
        json={
            "subject_id": "A-123",
            "org_id": "north",
            "classification": "restricted",
            "region": "midwest",
            "department": "finance",
            "payload": {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "record_type": "invoice",
                "status": "open",
                "priority": "high",
                "notes": "manual review",
            },
        },
    )
    assert response.status_code == 200
    record_id = response.json()["record_id"]

    analyst_token = token_for(client, "analyst_north", "Analyst123!")
    analyst_read = client.get(f"/records/{record_id}", headers={"Authorization": f"Bearer {analyst_token}"})
    assert analyst_read.status_code == 200
    payload = analyst_read.json()["payload"]
    assert payload["name"] == "REDACTED"
    assert payload["status"] == "open"


def test_audit_chain_verification(tmp_path: Path):
    client = build_client(tmp_path)
    admin_token = token_for(client, "admin", "ChangeMe123!")
    verify = client.get("/audit/verify", headers={"Authorization": f"Bearer {admin_token}"})
    assert verify.status_code == 200
    assert verify.json()["chain_valid"] is True


def test_key_rotation_endpoint(tmp_path: Path):
    client = build_client(tmp_path)
    admin_token = token_for(client, "admin", "ChangeMe123!")
    processor_token = token_for(client, "processor_north", "Processor123!")
    created = client.post(
        "/records",
        headers={"Authorization": f"Bearer {processor_token}"},
        json={
            "subject_id": "ROT-001",
            "org_id": "north",
            "classification": "restricted",
            "region": "midwest",
            "department": "ops",
            "payload": {"name": "Rot User", "email": "rot@example.com", "record_type": "claim", "status": "new", "priority": "low", "notes": "rotate"},
        },
    )
    assert created.status_code == 200
    rotated = client.post("/records/rotate-keys", headers={"Authorization": f"Bearer {admin_token}"})
    assert rotated.status_code == 200
    assert rotated.json()["records_reencrypted"] >= 1
