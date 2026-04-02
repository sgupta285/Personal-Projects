from fastapi import FastAPI
from fastapi.responses import ORJSONResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.services.runtime import runtime

configure_logging()
app = FastAPI(title=settings.app_name, default_response_class=ORJSONResponse)
app.include_router(api_router)


@app.on_event("startup")
def startup_event() -> None:
    runtime.load()


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)
