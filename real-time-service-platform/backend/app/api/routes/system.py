from fastapi import APIRouter, Request

from app.services.circuit_breaker import service_circuit_breaker

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/ready")
def ready():
    return {"ready": True}


@router.get("/trace")
def trace(request: Request):
    return {
        "correlation_id": request.state.correlation_id,
        "circuit_breaker": service_circuit_breaker.state,
    }
