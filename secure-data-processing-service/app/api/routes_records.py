from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import current_user
from app.models import RecordIn, RecordOut, UserContext
from app.services.processor import AccessDeniedError, ProcessorService

router = APIRouter(prefix="/records", tags=["records"])
@router.post("", response_model=dict)
def create_record(payload: RecordIn, user: UserContext = Depends(current_user)) -> dict[str, int]:
    service = ProcessorService()
    try:
        return {"record_id": service.create_record(user, payload)}
    except AccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/{record_id}", response_model=RecordOut)
def get_record(record_id: int, user: UserContext = Depends(current_user)) -> RecordOut:
    service = ProcessorService()
    try:
        return service.get_record(user, record_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post("/rotate-keys", response_model=dict)
def rotate_keys(user: UserContext = Depends(current_user)) -> dict:
    service = ProcessorService()
    try:
        return service.rotate_keys(user)
    except AccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
