from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

Role = Literal["admin", "processor", "analyst", "auditor"]
Classification = Literal["restricted", "confidential", "internal"]


class UserContext(BaseModel):
    username: str
    role: Role
    org_id: str
    allowed_tags: list[str] = Field(default_factory=list)


class RecordIn(BaseModel):
    subject_id: str = Field(min_length=3, max_length=128)
    org_id: str = Field(min_length=1, max_length=64)
    classification: Classification
    region: str = Field(min_length=2, max_length=32)
    department: str = Field(min_length=2, max_length=64)
    payload: dict[str, Any]

    @field_validator("payload")
    @classmethod
    def validate_payload(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("payload must not be empty")
        serialized = str(value)
        if "\x00" in serialized:
            raise ValueError("payload contains null bytes")
        return value


class RecordOut(BaseModel):
    id: int
    subject_id_hash: str
    org_id: str
    classification: Classification
    region: str
    department: str
    payload: dict[str, Any]
    created_by: str
    created_at: datetime


class LoginRequest(BaseModel):
    username: str
    password: str
    mfa_code: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int


class AuditEvent(BaseModel):
    ts: str
    actor: str
    action: str
    resource: str
    status: str
    metadata_json: dict[str, Any]
    prev_hash: str
    entry_hash: str
