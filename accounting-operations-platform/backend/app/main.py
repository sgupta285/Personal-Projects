from __future__ import annotations

from datetime import date
from io import BytesIO

from fastapi import FastAPI, File, HTTPException, UploadFile

from .db import init_db
from .repository import AccountingRepository
from .schemas import (
    AgingBucket,
    InvoiceCreate,
    InvoiceDetail,
    InvoiceRead,
    LiabilitySummary,
    SchedulePaymentRequest,
    VendorCreate,
    VendorRead,
    WorkflowAction,
)
from .services import AccountingService, WorkflowError

app = FastAPI(title="Accounting Operations Platform", version="1.0.0")
repo = AccountingRepository()
service = AccountingService(repo)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/vendors", response_model=VendorRead)
def create_vendor(payload: VendorCreate) -> dict:
    return service.create_vendor(**payload.model_dump())


@app.get("/vendors", response_model=list[VendorRead])
def list_vendors() -> list[dict]:
    return repo.list_vendors()


@app.post("/invoices", response_model=InvoiceRead)
def create_invoice(payload: InvoiceCreate) -> dict:
    try:
        return service.create_invoice(payload.model_dump(mode="json"), actor="api")
    except (WorkflowError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/invoices", response_model=list[InvoiceRead])
def list_invoices() -> list[dict]:
    return repo.list_invoices()


@app.get("/invoices/{invoice_id}", response_model=InvoiceDetail)
def get_invoice(invoice_id: int) -> dict:
    try:
        return service.invoice_detail(invoice_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/invoices/import-csv", response_model=list[InvoiceRead])
def import_csv(file: UploadFile = File(...)) -> list[dict]:
    try:
        payload = BytesIO(file.file.read())
        return service.import_csv(payload, actor="csv_import")
    except Exception as exc:  # pragma: no cover - defensive API guard
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/invoices/{invoice_id}/approve", response_model=InvoiceRead)
def approve(invoice_id: int, payload: WorkflowAction) -> dict:
    try:
        return service.approve_invoice(invoice_id, actor=payload.actor, notes=payload.notes)
    except (WorkflowError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/invoices/{invoice_id}/hold", response_model=InvoiceRead)
def hold(invoice_id: int, payload: WorkflowAction) -> dict:
    try:
        return service.hold_invoice(invoice_id, actor=payload.actor, notes=payload.notes)
    except (WorkflowError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/invoices/{invoice_id}/reject", response_model=InvoiceRead)
def reject(invoice_id: int, payload: WorkflowAction) -> dict:
    try:
        return service.reject_invoice(invoice_id, actor=payload.actor, notes=payload.notes)
    except (WorkflowError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/invoices/{invoice_id}/schedule-payment", response_model=InvoiceRead)
def schedule_payment(invoice_id: int, payload: SchedulePaymentRequest) -> dict:
    try:
        return service.schedule_payment(
            invoice_id=invoice_id,
            actor=payload.actor,
            payment_reference=payload.payment_reference,
            payment_method=payload.payment_method,
            payment_date=payload.payment_date.isoformat(),
            notes=payload.notes,
        )
    except (WorkflowError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/invoices/{invoice_id}/mark-paid", response_model=InvoiceRead)
def mark_paid(invoice_id: int, payload: WorkflowAction) -> dict:
    try:
        return service.mark_paid(invoice_id, actor=payload.actor, notes=payload.notes)
    except (WorkflowError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/reports/aging", response_model=list[AgingBucket])
def aging_report(reference_date: date | None = None) -> list[dict]:
    effective_date = (reference_date or date.today()).isoformat()
    return repo.aging_summary(effective_date)


@app.get("/reports/liabilities", response_model=LiabilitySummary)
def liabilities_report() -> dict:
    return repo.liability_summary()


@app.get("/reports/vendors/{vendor_id}")
def vendor_report(vendor_id: int) -> dict:
    try:
        return repo.vendor_breakdown(vendor_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
