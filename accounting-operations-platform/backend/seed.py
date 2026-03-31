from __future__ import annotations

from app.db import init_db
from app.services import AccountingService


def main() -> None:
    init_db()
    service = AccountingService()
    vendor = service.create_vendor("North Ridge Supply", "ap@northridge.example", 30)
    invoice = service.create_invoice(
        {
            "vendor_id": vendor["id"],
            "vendor_invoice_number": "NR-1001",
            "invoice_date": "2026-03-01",
            "due_date": "2026-03-31",
            "currency": "USD",
            "amount": 1825.45,
            "description": "Office networking hardware",
            "notes": "Initial seed invoice",
        },
        actor="seed",
    )
    service.approve_invoice(invoice["id"], actor="seed-reviewer", notes="Approved in sample data")
    print("Seeded sample vendor and invoice data.")


if __name__ == "__main__":
    main()
