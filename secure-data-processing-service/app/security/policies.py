from __future__ import annotations

from typing import Any

from app.models import UserContext


COLUMN_POLICIES = {
    "admin": None,
    "processor": {"name", "email", "notes", "status", "priority", "record_type"},
    "analyst": {"status", "priority", "record_type"},
    "auditor": {"status", "priority", "record_type", "notes"},
}


def can_access_row(user: UserContext, record_org: str) -> bool:
    if user.role in {"admin", "auditor"}:
        return True
    return user.org_id == record_org


def redact_payload(user: UserContext, payload: dict[str, Any]) -> dict[str, Any]:
    allowed = COLUMN_POLICIES.get(user.role)
    if allowed is None:
        return payload
    result: dict[str, Any] = {}
    for key, value in payload.items():
        result[key] = value if key in allowed else "REDACTED"
    return result
