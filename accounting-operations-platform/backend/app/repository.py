from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Iterable

from .db import get_connection


UTC_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime(UTC_FORMAT)


class AccountingRepository:
    def create_vendor(self, name: str, contact_email: str | None, payment_terms_days: int) -> dict:
        now = utcnow()
        conn = get_connection()
        try:
            cursor = conn.execute(
                "INSERT INTO vendors(name, contact_email, payment_terms_days, created_at) VALUES (?, ?, ?, ?)",
                (name, contact_email, payment_terms_days, now),
            )
            conn.commit()
            return self.get_vendor(cursor.lastrowid)
        finally:
            conn.close()

    def get_vendor(self, vendor_id: int) -> dict:
        conn = get_connection()
        try:
            row = conn.execute("SELECT * FROM vendors WHERE id = ?", (vendor_id,)).fetchone()
            if row is None:
                raise KeyError(f"Vendor {vendor_id} not found")
            return dict(row)
        finally:
            conn.close()

    def list_vendors(self) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM vendors ORDER BY name ASC").fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def find_vendor_by_name(self, name: str) -> dict | None:
        conn = get_connection()
        try:
            row = conn.execute("SELECT * FROM vendors WHERE name = ?", (name,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def create_invoice(self, payload: dict) -> dict:
        now = utcnow()
        conn = get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO invoices(
                    vendor_id, vendor_invoice_number, invoice_date, due_date, currency, amount,
                    status, description, notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["vendor_id"],
                    payload["vendor_invoice_number"],
                    payload["invoice_date"],
                    payload["due_date"],
                    payload["currency"],
                    payload["amount"],
                    payload["status"],
                    payload.get("description"),
                    payload.get("notes"),
                    now,
                    now,
                ),
            )
            invoice_id = cursor.lastrowid
            conn.commit()
            return self.get_invoice(invoice_id)
        finally:
            conn.close()

    def get_invoice(self, invoice_id: int) -> dict:
        conn = get_connection()
        try:
            row = conn.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
            if row is None:
                raise KeyError(f"Invoice {invoice_id} not found")
            return dict(row)
        finally:
            conn.close()

    def list_invoices(self) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM invoices ORDER BY created_at DESC, id DESC").fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def update_invoice_status(self, invoice_id: int, status: str) -> dict:
        conn = get_connection()
        try:
            conn.execute(
                "UPDATE invoices SET status = ?, updated_at = ? WHERE id = ?",
                (status, utcnow(), invoice_id),
            )
            conn.commit()
            return self.get_invoice(invoice_id)
        finally:
            conn.close()

    def invoice_exists(self, vendor_id: int, vendor_invoice_number: str) -> bool:
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT 1 FROM invoices WHERE vendor_id = ? AND vendor_invoice_number = ?",
                (vendor_id, vendor_invoice_number),
            ).fetchone()
            return row is not None
        finally:
            conn.close()

    def add_audit_event(self, invoice_id: int, actor: str, event_type: str, notes: str | None) -> dict:
        conn = get_connection()
        try:
            cursor = conn.execute(
                "INSERT INTO audit_events(invoice_id, actor, event_type, notes, created_at) VALUES (?, ?, ?, ?, ?)",
                (invoice_id, actor, event_type, notes, utcnow()),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM audit_events WHERE id = ?", (cursor.lastrowid,)).fetchone()
            return dict(row)
        finally:
            conn.close()

    def list_audit_events(self, invoice_id: int) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM audit_events WHERE invoice_id = ? ORDER BY id ASC",
                (invoice_id,),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def add_payment(self, invoice_id: int, payment_reference: str, payment_method: str, payment_date: str, amount_paid: float) -> dict:
        conn = get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO payments(invoice_id, payment_reference, payment_method, payment_date, amount_paid, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (invoice_id, payment_reference, payment_method, payment_date, amount_paid, utcnow()),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM payments WHERE id = ?", (cursor.lastrowid,)).fetchone()
            return dict(row)
        finally:
            conn.close()

    def list_payments(self, invoice_id: int) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM payments WHERE invoice_id = ? ORDER BY id ASC",
                (invoice_id,),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def aging_summary(self, reference_date: str) -> list[dict]:
        conn = get_connection()
        try:
            query = """
            SELECT
                CASE
                    WHEN julianday(?) - julianday(due_date) <= 0 THEN 'current'
                    WHEN julianday(?) - julianday(due_date) BETWEEN 1 AND 30 THEN '1_30_days'
                    WHEN julianday(?) - julianday(due_date) BETWEEN 31 AND 60 THEN '31_60_days'
                    ELSE '61_plus_days'
                END AS bucket,
                COUNT(*) AS count,
                ROUND(SUM(amount), 2) AS total_amount
            FROM invoices
            WHERE status IN ('pending_review', 'on_hold', 'approved', 'scheduled_for_payment')
            GROUP BY bucket
            ORDER BY bucket ASC
            """
            rows = conn.execute(query, (reference_date, reference_date, reference_date)).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def liability_summary(self) -> dict:
        conn = get_connection()
        try:
            open_rows = conn.execute(
                "SELECT COUNT(*) AS count, ROUND(COALESCE(SUM(amount), 0), 2) AS total FROM invoices WHERE status IN ('pending_review', 'on_hold', 'approved', 'scheduled_for_payment')"
            ).fetchone()
            approved_rows = conn.execute(
                "SELECT COUNT(*) AS count, ROUND(COALESCE(SUM(amount), 0), 2) AS total FROM invoices WHERE status IN ('approved', 'scheduled_for_payment')"
            ).fetchone()
            return {
                "open_invoice_count": open_rows["count"],
                "open_liability_amount": open_rows["total"],
                "approved_invoice_count": approved_rows["count"],
                "approved_but_unpaid_amount": approved_rows["total"],
            }
        finally:
            conn.close()

    def vendor_breakdown(self, vendor_id: int) -> dict:
        conn = get_connection()
        try:
            vendor = self.get_vendor(vendor_id)
            rows = conn.execute(
                "SELECT status, COUNT(*) AS count, ROUND(COALESCE(SUM(amount), 0), 2) AS total_amount FROM invoices WHERE vendor_id = ? GROUP BY status ORDER BY status ASC",
                (vendor_id,),
            ).fetchall()
            return {
                "vendor": vendor,
                "status_breakdown": [dict(row) for row in rows],
            }
        finally:
            conn.close()
