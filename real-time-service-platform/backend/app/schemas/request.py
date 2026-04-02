from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ServiceRequestCreate(BaseModel):
    kind: str = Field(min_length=3, max_length=50)
    payload: dict[str, Any]
    priority: int = Field(default=3, ge=1, le=5)


class ServiceRequestRead(BaseModel):
    id: int
    kind: str
    status: str
    priority: int
    downstream_latency_ms: float
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobSubmitResponse(BaseModel):
    request_id: int
    status: str
    correlation_id: str
