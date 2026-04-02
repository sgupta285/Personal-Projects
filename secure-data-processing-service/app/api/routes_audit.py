from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import current_user
from app.database import fetch_all
from app.models import UserContext
from app.services.audit import AuditService
from app.services.compliance import ComplianceService

router = APIRouter(prefix="/audit", tags=["audit"])
@router.get("/events")
def events(user: UserContext = Depends(current_user)) -> dict:
    if user.role not in {"admin", "auditor"}:
        raise HTTPException(status_code=403, detail="audit access requires admin or auditor role")
    rows = fetch_all("SELECT * FROM audit_events ORDER BY id DESC LIMIT 200")
    return {"events": [dict(row) for row in rows]}


@router.get("/verify")
def verify(user: UserContext = Depends(current_user)) -> dict[str, bool]:
    if user.role not in {"admin", "auditor"}:
        raise HTTPException(status_code=403, detail="audit verification requires admin or auditor role")
    return {"chain_valid": AuditService().verify_chain()}


@router.get("/compliance-report")
def report(user: UserContext = Depends(current_user)) -> dict:
    if user.role not in {"admin", "auditor"}:
        raise HTTPException(status_code=403, detail="compliance reporting requires admin or auditor role")
    return ComplianceService().generate_summary()
