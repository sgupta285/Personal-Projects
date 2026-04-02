from datetime import datetime
from pydantic import BaseModel, Field


class ErrorEnvelope(BaseModel):
    error: dict[str, str]


class PaginationMeta(BaseModel):
    total: int
    page: int | None = None
    page_size: int | None = None
    next_cursor: str | None = None


class RequestContext(BaseModel):
    request_id: str
    client_id: str
    scopes: list[str] = Field(default_factory=list)
    token_type: str


class AuditStamp(BaseModel):
    created_at: datetime
    updated_at: datetime
