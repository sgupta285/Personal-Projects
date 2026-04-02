from fastapi import APIRouter

from ..metrics import metrics_response

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/metrics")
def metrics():
    return metrics_response()
