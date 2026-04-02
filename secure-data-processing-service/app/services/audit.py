from __future__ import annotations

import hashlib
import json
from typing import Any

from app.config import settings
from app.database import execute, fetch_all, fetch_one, now_iso


class AuditService:
    def __init__(self, path=None):
        self.path = path or settings.audit_log_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text('', encoding='utf-8')

    def _last_hash(self) -> str:
        row = fetch_one("SELECT entry_hash FROM audit_events ORDER BY id DESC LIMIT 1")
        return row["entry_hash"] if row else "GENESIS"

    def log(self, actor: str, action: str, resource: str, status: str, metadata: dict[str, Any]) -> str:
        ts = now_iso()
        prev = self._last_hash()
        canonical = json.dumps({
            "ts": ts,
            "actor": actor,
            "action": action,
            "resource": resource,
            "status": status,
            "metadata": metadata,
            "prev_hash": prev,
        }, sort_keys=True)
        entry_hash = hashlib.sha256(canonical.encode()).hexdigest()
        execute(
            "INSERT INTO audit_events (ts, actor, action, resource, status, metadata_json, prev_hash, entry_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (ts, actor, action, resource, status, json.dumps(metadata, sort_keys=True), prev, entry_hash),
        )
        with self.path.open("a", encoding="utf-8") as handle:
            entry = {"ts": ts, "actor": actor, "action": action, "resource": resource, "status": status, "metadata": metadata, "prev_hash": prev, "entry_hash": entry_hash}
            handle.write(json.dumps(entry, sort_keys=True) + "\n")
        return entry_hash

    def verify_chain(self) -> bool:
        rows = fetch_all("SELECT * FROM audit_events ORDER BY id ASC")
        prev = "GENESIS"
        for row in rows:
            canonical = json.dumps({
                "ts": row["ts"],
                "actor": row["actor"],
                "action": row["action"],
                "resource": row["resource"],
                "status": row["status"],
                "metadata": json.loads(row["metadata_json"]),
                "prev_hash": prev,
            }, sort_keys=True)
            expected = hashlib.sha256(canonical.encode()).hexdigest()
            if row["prev_hash"] != prev or row["entry_hash"] != expected:
                return False
            prev = row["entry_hash"]
        return True
