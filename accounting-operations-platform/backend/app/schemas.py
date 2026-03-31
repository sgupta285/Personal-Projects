from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, EmailStr

InvoiceStatus = Literal[
    "pending_review",
    "on_hold",
    "rejected",
    "approved",
    "scheduled_for_payment",
    "paid",
]


class VendorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    contact_email: EmailStr | None = None
    payment_terms_days: int = Field(default=30, ge=0, le=365)


class VendorRead(VendorCreate):
    id: int
    created_at: str


class InvoiceCreate(BaseModel):
    vendor_id: int
    vendor_invoice_number: str = Field(min_length=1, max_length=100)
    invoice_date: date
    due_date: date
    currency: str = Field(default="USD", min_length=3, max_length=3)
    amount: float = Field(gt=0)
    description: str | None = None
    notes: str | None = None


class InvoiceRead(InvoiceCreate):
    id: int
    status: InvoiceStatus
    created_at: str
    updated_at: str


class WorkflowAction(BaseModel):
    actor: str = Field(min_length=1, max_length=100)
    notes: str | None = None


class SchedulePaymentRequest(WorkflowAction):
    payment_reference: str = Field(min_length=1, max_length=100)
    payment_method: str = Field(min_length=1, max_length=50)
    payment_date: date


class PaymentRead(BaseModel):
    id: int
    invoice_id: int
    payment_reference: str
    payment_method: str
    payment_date: str
    amount_paid: float
    created_at: str


class AuditEventRead(BaseModel):
    id: int
    invoice_id: int
    actor: str
    event_type: str
    notes: str | None = None
    created_at: str


class InvoiceDetail(BaseModel):
    invoice: InvoiceRead
    payments: list[PaymentRead]
    audit_events: list[AuditEventRead]


class AgingBucket(BaseModel):
    bucket: str
    count: int
    total_amount: float


class LiabilitySummary(BaseModel):
    open_invoice_count: int
    open_liability_amount: float
    approved_invoice_count: int
    approved_but_unpaid_amount: float
