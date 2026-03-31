from fastapi import FastAPI

from app.api.routes_datasets import router as datasets_router
from app.api.routes_prompts import router as prompts_router
from app.api.routes_reports import router as reports_router
from app.api.routes_runs import router as runs_router
from app.config import settings
from app.db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.include_router(datasets_router)
app.include_router(prompts_router)
app.include_router(runs_router)
app.include_router(reports_router)


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "status": "ok",
        "docs": "/docs",
        "default_provider": settings.default_provider,
    }
