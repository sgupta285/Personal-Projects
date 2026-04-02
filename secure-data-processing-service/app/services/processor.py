from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from app.database import execute, fetch_all, fetch_one
from app.models import RecordIn, RecordOut, UserContext
from app.security.encryption import LocalKMS
from app.security.policies import can_access_row, redact_payload
from app.services.audit import AuditService


class AccessDeniedError(Exception):
    pass


class ProcessorService:
    def __init__(self, kms: LocalKMS | None = None, audit: AuditService | None = None):
        self.kms = kms or LocalKMS()
        self.audit = audit or AuditService()

    @staticmethod
    def _hash_subject(subject_id: str) -> str:
        return hashlib.sha256(subject_id.strip().lower().encode()).hexdigest()

    @staticmethod
    def _sanitize_payload(payload: dict[str, Any]) -> dict[str, Any]:
        cleaned: dict[str, Any] = {}
        for key, value in payload.items():
            if isinstance(value, str):
                cleaned[key] = value.replace("\x00", "").strip()
            else:
                cleaned[key] = value
        return cleaned

    def create_record(self, actor: UserContext, record: RecordIn) -> int:
        if actor.role not in {"admin", "processor"}:
            self.audit.log(actor.username, "create_record", "record", "denied", {"org_id": record.org_id})
            raise AccessDeniedError("user cannot create restricted records")
        cleaned = record.model_copy(update={"payload": self._sanitize_payload(record.payload)})
        key_id, token = self.kms.encrypt_json(cleaned.payload)
        record_id = execute(
            "INSERT INTO records (subject_id_hash, org_id, classification, region, department, kms_key_id, encrypted_payload, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))",
            (
                self._hash_subject(cleaned.subject_id),
                cleaned.org_id,
                cleaned.classification,
                cleaned.region,
                cleaned.department,
                key_id,
                token,
                actor.username,
            ),
        )
        self.audit.log(actor.username, "create_record", f"record:{record_id}", "success", {"classification": cleaned.classification, "org_id": cleaned.org_id})
        return record_id

    def get_record(self, actor: UserContext, record_id: int) -> RecordOut:
        row = fetch_one("SELECT * FROM records WHERE id = ?", (record_id,))
        if not row:
            self.audit.log(actor.username, "read_record", f"record:{record_id}", "not_found", {})
            raise KeyError("record not found")
        if not can_access_row(actor, row["org_id"]):
            self.audit.log(actor.username, "read_record", f"record:{record_id}", "denied", {"org_id": row["org_id"]})
            raise AccessDeniedError("row-level policy denied access")
        payload = self.kms.decrypt_json(row["kms_key_id"], row["encrypted_payload"])
        visible_payload = redact_payload(actor, payload)
        self.audit.log(actor.username, "read_record", f"record:{record_id}", "success", {"org_id": row["org_id"], "classification": row["classification"]})
        return RecordOut(
            id=row["id"],
            subject_id_hash=row["subject_id_hash"],
            org_id=row["org_id"],
            classification=row["classification"],
            region=row["region"],
            department=row["department"],
            payload=visible_payload,
            created_by=row["created_by"],
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")) if "T" in row["created_at"] else datetime.fromisoformat(row["created_at"]),
        )

    def rotate_keys(self, actor: UserContext) -> dict[str, Any]:
        if actor.role != "admin":
            self.audit.log(actor.username, "rotate_keys", "kms", "denied", {})
            raise AccessDeniedError("only admin can rotate keys")
        old_key_id, new_key_id = self.kms.rotate()
        rows = fetch_all("SELECT id, kms_key_id, encrypted_payload FROM records WHERE kms_key_id = ?", (old_key_id,))
        for row in rows:
            payload = self.kms.decrypt_json(old_key_id, row["encrypted_payload"])
            fresh_key_id, token = self.kms.encrypt_json(payload)
            execute("UPDATE records SET kms_key_id = ?, encrypted_payload = ? WHERE id = ?", (fresh_key_id, token, row["id"]))
        execute(
            "INSERT INTO key_rotations (old_key_id, new_key_id, rotated_at, records_reencrypted) VALUES (?, ?, datetime('now'), ?)",
            (old_key_id, new_key_id, len(rows)),
        )
        self.audit.log(actor.username, "rotate_keys", "kms", "success", {"old_key_id": old_key_id, "new_key_id": new_key_id, "records_reencrypted": len(rows)})
        return {"old_key_id": old_key_id, "new_key_id": new_key_id, "records_reencrypted": len(rows)}
