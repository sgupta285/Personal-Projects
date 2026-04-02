from fastapi import APIRouter

from app.api.routes import experiments, health, recommendations

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(recommendations.router, prefix="/v1/recommendations", tags=["recommendations"])
api_router.include_router(experiments.router, prefix="/v1/experiments", tags=["experiments"])
