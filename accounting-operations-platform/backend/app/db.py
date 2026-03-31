from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "accounting_ops.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS vendors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                contact_email TEXT,
                payment_terms_days INTEGER NOT NULL DEFAULT 30,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_id INTEGER NOT NULL,
                vendor_invoice_number TEXT NOT NULL,
                invoice_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                currency TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                description TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(vendor_id, vendor_invoice_number),
                FOREIGN KEY(vendor_id) REFERENCES vendors(id)
            );

            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL UNIQUE,
                payment_reference TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                payment_date TEXT NOT NULL,
                amount_paid REAL NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(invoice_id) REFERENCES invoices(id)
            );

            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                actor TEXT NOT NULL,
                event_type TEXT NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(invoice_id) REFERENCES invoices(id)
            );
            """
        )
        conn.commit()
    finally:
        conn.close()
