from fastapi import APIRouter

from app.services.runtime import runtime

router = APIRouter(prefix="/health")


@router.get("/live")
def live() -> dict:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict:
    return {"status": "ready", "artifacts_loaded": runtime.is_loaded}
