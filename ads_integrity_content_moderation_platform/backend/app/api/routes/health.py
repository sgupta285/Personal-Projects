from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health", summary="Health check")
def health():
    return {"status": "ok", "app_env": settings.app_env}
