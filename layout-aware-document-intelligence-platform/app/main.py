
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.db.base import Base
from app.models import Document, DocumentRevision, ParseJob  # noqa: F401
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.ensure_dirs()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
    description="A deterministic document parsing service focused on layout, reading order, sections, tables, and structured outputs.",
)
app.include_router(router)
