from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from app import db
from app.repository import AccountingRepository
from app.services import AccountingService, WorkflowError


class AccountingWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        db.DB_PATH = Path(self.temp_dir.name) / "test.db"
        db.init_db()
        self.service = AccountingService(AccountingRepository())

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _create_vendor_and_invoice(self) -> tuple[dict, dict]:
        vendor = self.service.create_vendor("Acme Parts", "ap@acme.example", 30)
        invoice = self.service.create_invoice(
            {
                "vendor_id": vendor["id"],
                "vendor_invoice_number": "INV-001",
                "invoice_date": "2026-03-01",
                "due_date": "2026-03-15",
                "currency": "USD",
                "amount": 500.0,
                "description": "Replacement parts",
                "notes": "Urgent",
            },
            actor="tester",
        )
        return vendor, invoice

    def test_create_vendor_and_invoice(self) -> None:
        vendor, invoice = self._create_vendor_and_invoice()
        self.assertEqual(vendor["name"], "Acme Parts")
        self.assertEqual(invoice["status"], "pending_review")

    def test_duplicate_invoice_rejected(self) -> None:
        vendor, _ = self._create_vendor_and_invoice()
        with self.assertRaises(WorkflowError):
            self.service.create_invoice(
                {
                    "vendor_id": vendor["id"],
                    "vendor_invoice_number": "INV-001",
                    "invoice_date": "2026-03-02",
                    "due_date": "2026-03-20",
                    "currency": "USD",
                    "amount": 700.0,
                },
                actor="tester",
            )

    def test_full_payment_workflow(self) -> None:
        _, invoice = self._create_vendor_and_invoice()
        approved = self.service.approve_invoice(invoice["id"], actor="manager", notes="Looks good")
        self.assertEqual(approved["status"], "approved")
        scheduled = self.service.schedule_payment(
            approved["id"],
            actor="accounting",
            payment_reference="ACH-123",
            payment_method="ACH",
            payment_date="2026-03-16",
            notes="weekly batch",
        )
        self.assertEqual(scheduled["status"], "scheduled_for_payment")
        paid = self.service.mark_paid(invoice["id"], actor="treasury", notes="remitted")
        self.assertEqual(paid["status"], "paid")
        detail = self.service.invoice_detail(invoice["id"])
        self.assertEqual(len(detail["payments"]), 1)
        self.assertGreaterEqual(len(detail["audit_events"]), 4)

    def test_invalid_transition(self) -> None:
        _, invoice = self._create_vendor_and_invoice()
        with self.assertRaises(WorkflowError):
            self.service.mark_paid(invoice["id"], actor="treasury")

    def test_liability_summary(self) -> None:
        _, invoice = self._create_vendor_and_invoice()
        self.service.approve_invoice(invoice["id"], actor="manager")
        summary = self.service.repo.liability_summary()
        self.assertEqual(summary["approved_invoice_count"], 1)
        self.assertEqual(summary["approved_but_unpaid_amount"], 500.0)


if __name__ == "__main__":
    unittest.main()
