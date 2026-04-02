import json

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.security import RoleChecker, get_current_user
from app.db.database import get_db
from app.db.models import ServiceRequest, User
from app.schemas.request import JobSubmitResponse, ServiceRequestCreate, ServiceRequestRead
from app.services.request_service import RequestService

router = APIRouter()


@router.post("/sync", response_model=ServiceRequestRead)
def submit_sync(
    payload: ServiceRequestCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = RequestService(db)
    record = service.create_request(user, payload.kind, payload.payload, payload.priority)
    return service.execute_sync(record, payload.payload)


@router.post("/async", response_model=JobSubmitResponse)
def submit_async(
    payload: ServiceRequestCreate,
    http_request: Request,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = RequestService(db)
    record = service.create_request(user, payload.kind, payload.payload, payload.priority)
    service.enqueue_async(background_tasks, record, payload.payload)
    return JobSubmitResponse(
        request_id=record.id,
        status="queued",
        correlation_id=http_request.state.correlation_id,
    )


@router.get("/{request_id}", response_model=ServiceRequestRead)
def get_request(
    request_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.get(ServiceRequest, request_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Request not found")
    if user.role != "admin" and record.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return record


@router.get("/", response_model=list[ServiceRequestRead])
def list_requests(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(ServiceRequest).order_by(ServiceRequest.created_at.desc())
    if user.role != "admin":
        query = query.filter(ServiceRequest.owner_id == user.id)
    return query.limit(100).all()


@router.get("/admin/all", response_model=list[ServiceRequestRead])
def admin_list_requests(
    _admin: User = Depends(RoleChecker("admin")),
    db: Session = Depends(get_db),
):
    return db.query(ServiceRequest).order_by(ServiceRequest.created_at.desc()).limit(200).all()
