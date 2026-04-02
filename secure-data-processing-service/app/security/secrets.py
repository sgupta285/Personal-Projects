from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.config import settings


class LocalSecretsManager:
    def __init__(self, path: Path | None = None):
        self.path = path or settings.local_secrets_file
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({"db_password": "local-dev-password", "signing_salt": "local-dev-salt"}, indent=2), encoding="utf-8")

    def get_secret(self, name: str) -> str:
        data: dict[str, Any] = json.loads(self.path.read_text(encoding="utf-8"))
        if name not in data:
            raise KeyError(f"secret {name} not found")
        return str(data[name])

    def set_secret(self, name: str, value: str) -> None:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        data[name] = value
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
