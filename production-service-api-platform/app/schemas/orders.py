from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.common import AuditStamp


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=120)
    item_sku: str = Field(min_length=3, max_length=64)
    quantity: int = Field(ge=1, le=1000)
    total_cents: int = Field(ge=1)
    notes: str | None = Field(default=None, max_length=1000)


class OrderUpdate(BaseModel):
    status: str = Field(pattern='^(pending|fulfilled|cancelled)$')
    notes: str | None = Field(default=None, max_length=1000)


class OrderRead(BaseModel):
    id: int
    external_id: str
    customer_name: str
    item_sku: str
    quantity: int
    status: str
    total_cents: int
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}


class OrderReadV2(OrderRead):
    links: dict[str, str]
    audit: AuditStamp
