from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class FailureMode(str, Enum):
    NONE = "none"
    TRANSIENT_ONCE = "transient_once"
    ALWAYS = "always"


class EventIn(BaseModel):
    event_id: str = Field(min_length=3)
    entity_id: str = Field(min_length=1)
    event_type: str = Field(min_length=1)
    occurred_at: datetime
    payload: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str = Field(min_length=3)
    failure_mode: FailureMode = FailureMode.NONE

    @field_validator("occurred_at")
    @classmethod
    def ensure_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


class EventBatchIn(BaseModel):
    events: list[EventIn]


class IngestResponse(BaseModel):
    accepted: int
    duplicates: int
    queued_partitions: list[int]


class StatusResponse(BaseModel):
    queue_depth: int
    partitions: dict[int, int]
    metrics: dict[str, Any]
    autoscaler: dict[str, Any]


class DLQRecord(BaseModel):
    dlq_id: str
    event_id: str
    entity_id: str
    attempts: int
    last_error: str
    created_at: str


class ReplayResponse(BaseModel):
    replayed: bool
    dlq_id: str
    target_partition: int
