from __future__ import annotations

import csv
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import BinaryIO

from .repository import AccountingRepository

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "pending_review": {"on_hold", "rejected", "approved"},
    "on_hold": {"pending_review", "rejected", "approved"},
    "rejected": set(),
    "approved": {"scheduled_for_payment", "paid"},
    "scheduled_for_payment": {"paid"},
    "paid": set(),
}


class WorkflowError(ValueError):
    pass


class AccountingService:
    def __init__(self, repo: AccountingRepository | None = None) -> None:
        self.repo = repo or AccountingRepository()

    def create_vendor(self, name: str, contact_email: str | None, payment_terms_days: int) -> dict:
        existing = self.repo.find_vendor_by_name(name)
        if existing:
            return existing
        return self.repo.create_vendor(name=name, contact_email=contact_email, payment_terms_days=payment_terms_days)

    def create_invoice(self, payload: dict, actor: str = "system") -> dict:
        vendor = self.repo.get_vendor(payload["vendor_id"])
        if self.repo.invoice_exists(vendor["id"], payload["vendor_invoice_number"]):
            raise WorkflowError("Duplicate vendor invoice number for this vendor")
        invoice = self.repo.create_invoice({**payload, "status": "pending_review"})
        self.repo.add_audit_event(invoice["id"], actor, "invoice_created", payload.get("notes"))
        return invoice

    def transition_invoice(self, invoice_id: int, new_status: str, actor: str, notes: str | None = None) -> dict:
        invoice = self.repo.get_invoice(invoice_id)
        if new_status not in ALLOWED_TRANSITIONS[invoice["status"]]:
            raise WorkflowError(f"Cannot transition invoice from {invoice['status']} to {new_status}")
        updated = self.repo.update_invoice_status(invoice_id, new_status)
        self.repo.add_audit_event(invoice_id, actor, f"status_changed_to_{new_status}", notes)
        return updated

    def approve_invoice(self, invoice_id: int, actor: str, notes: str | None = None) -> dict:
        return self.transition_invoice(invoice_id, "approved", actor, notes)

    def hold_invoice(self, invoice_id: int, actor: str, notes: str | None = None) -> dict:
        return self.transition_invoice(invoice_id, "on_hold", actor, notes)

    def reject_invoice(self, invoice_id: int, actor: str, notes: str | None = None) -> dict:
        return self.transition_invoice(invoice_id, "rejected", actor, notes)

    def schedule_payment(self, invoice_id: int, actor: str, payment_reference: str, payment_method: str, payment_date: str, notes: str | None = None) -> dict:
        updated = self.transition_invoice(invoice_id, "scheduled_for_payment", actor, notes)
        self.repo.add_payment(
            invoice_id=invoice_id,
            payment_reference=payment_reference,
            payment_method=payment_method,
            payment_date=payment_date,
            amount_paid=updated["amount"],
        )
        self.repo.add_audit_event(invoice_id, actor, "payment_scheduled", f"{payment_method}:{payment_reference}")
        return self.repo.get_invoice(invoice_id)

    def mark_paid(self, invoice_id: int, actor: str, notes: str | None = None) -> dict:
        invoice = self.repo.get_invoice(invoice_id)
        if invoice["status"] not in {"approved", "scheduled_for_payment"}:
            raise WorkflowError("Only approved or scheduled invoices can be marked paid")
        updated = self.repo.update_invoice_status(invoice_id, "paid")
        self.repo.add_audit_event(invoice_id, actor, "payment_completed", notes)
        return updated

    def invoice_detail(self, invoice_id: int) -> dict:
        return {
            "invoice": self.repo.get_invoice(invoice_id),
            "payments": self.repo.list_payments(invoice_id),
            "audit_events": self.repo.list_audit_events(invoice_id),
        }

    def import_csv(self, file_like: BinaryIO, actor: str = "importer") -> list[dict]:
        decoded = file_like.read().decode("utf-8")
        reader = csv.DictReader(decoded.splitlines())
        imported: list[dict] = []
        for row in reader:
            vendor = self.create_vendor(
                name=row["vendor_name"],
                contact_email=row.get("vendor_email") or None,
                payment_terms_days=int(row.get("payment_terms_days") or 30),
            )
            invoice = self.create_invoice(
                {
                    "vendor_id": vendor["id"],
                    "vendor_invoice_number": row["vendor_invoice_number"],
                    "invoice_date": row["invoice_date"],
                    "due_date": row["due_date"],
                    "currency": row.get("currency", "USD") or "USD",
                    "amount": float(row["amount"]),
                    "description": row.get("description") or None,
                    "notes": row.get("notes") or None,
                },
                actor=actor,
            )
            imported.append(invoice)
        return imported
