from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet

from app.config import settings


@dataclass
class KeyRecord:
    key_id: str
    key_material: str
    created_at: str


class LocalKMS:
    def __init__(self, path: Path | None = None):
        self.path = path or settings.local_kms_key_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            initial = self._new_key("cmk-001")
            self._save({"active_key_id": initial.key_id, "keys": [initial.__dict__]})

    def _load(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _new_key(self, key_id: str) -> KeyRecord:
        return KeyRecord(key_id=key_id, key_material=Fernet.generate_key().decode(), created_at=datetime.now(timezone.utc).isoformat())

    def active_key_id(self) -> str:
        return self._load()["active_key_id"]

    def _fernet(self, key_id: str) -> Fernet:
        data = self._load()
        match = next(item for item in data["keys"] if item["key_id"] == key_id)
        return Fernet(match["key_material"].encode())

    def encrypt_json(self, payload: dict[str, Any]) -> tuple[str, str]:
        key_id = self.active_key_id()
        token = self._fernet(key_id).encrypt(json.dumps(payload, sort_keys=True).encode()).decode()
        return key_id, token

    def decrypt_json(self, key_id: str, token: str) -> dict[str, Any]:
        raw = self._fernet(key_id).decrypt(token.encode())
        return json.loads(raw)

    def rotate(self) -> tuple[str, str]:
        data = self._load()
        current = data["active_key_id"]
        next_id = f"cmk-{len(data['keys']) + 1:03d}"
        record = self._new_key(next_id)
        data["keys"].append(record.__dict__)
        data["active_key_id"] = next_id
        self._save(data)
        return current, next_id
