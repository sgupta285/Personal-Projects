from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app import db
from backend.app.repository import AccountingRepository
from backend.app.services import AccountingService


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "smoke.db"
        db.init_db()
        service = AccountingService(AccountingRepository())
        vendor = service.create_vendor("Harbor Electric", "ap@harbor.example", 30)
        invoice = service.create_invoice(
            {
                "vendor_id": vendor["id"],
                "vendor_invoice_number": "HB-9001",
                "invoice_date": "2026-03-01",
                "due_date": "2026-03-29",
                "currency": "USD",
                "amount": 2500.0,
                "description": "Panel upgrade",
                "notes": "smoke test",
            },
            actor="smoke",
        )
        service.approve_invoice(invoice["id"], actor="controller")
        service.schedule_payment(invoice["id"], actor="ap", payment_reference="ACH-009", payment_method="ACH", payment_date="2026-03-30")
        service.mark_paid(invoice["id"], actor="treasury")
        detail = service.invoice_detail(invoice["id"])
        print({
            "invoice_status": detail["invoice"]["status"],
            "payment_count": len(detail["payments"]),
            "audit_count": len(detail["audit_events"]),
        })


if __name__ == "__main__":
    main()
