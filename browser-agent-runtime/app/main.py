from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.runs import router as runs_router
from app.api.tasks import router as tasks_router
from app.db import Base, engine
from app.utils.logging import configure_logging

configure_logging()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Browser Agent Runtime",
    version="0.1.0",
    description="Control plane and worker-facing APIs for replayable browser agent execution.",
)

app.include_router(health_router)
app.include_router(tasks_router)
app.include_router(runs_router)
