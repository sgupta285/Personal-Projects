from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Vendor:
    id: int
    name: str
    contact_email: str | None
    payment_terms_days: int
    created_at: str


@dataclass(slots=True)
class Invoice:
    id: int
    vendor_id: int
    vendor_invoice_number: str
    invoice_date: str
    due_date: str
    currency: str
    amount: float
    status: str
    description: str | None
    notes: str | None
    created_at: str
    updated_at: str


@dataclass(slots=True)
class Payment:
    id: int
    invoice_id: int
    payment_reference: str
    payment_method: str
    payment_date: str
    amount_paid: float
    created_at: str


@dataclass(slots=True)
class AuditEvent:
    id: int
    invoice_id: int
    actor: str
    event_type: str
    notes: str | None
    created_at: str
