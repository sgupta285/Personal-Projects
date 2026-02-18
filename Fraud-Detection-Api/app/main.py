"""
Fraud Detection API — Main Application
Low-latency ML inference with caching, circuit breaker, and drift monitoring.
"""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.api.routes import router
from app.services.inference import model_service
from app.services.cache import cache_service
from app.monitoring.drift import drift_monitor
from app.monitoring.metrics import MODEL_LOADED

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("starting_up", app=settings.app_name, version=settings.app_version)

    # Load model
    loaded = model_service.load()
    MODEL_LOADED.set(1 if loaded else 0)
    if not loaded:
        logger.warning("model_not_loaded", hint="Run 'python -m app.models.train' first")

    # Connect cache
    cache_service.connect()

    # Initialize drift monitor with synthetic reference distribution
    drift_monitor.generate_reference_from_uniform()

    logger.info("startup_complete", model_loaded=loaded, cache=cache_service.is_available)

    yield

    # Shutdown
    logger.info("shutting_down")
    cache_service.disconnect()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production fraud scoring API with low-latency ML inference, Redis caching, "
                "circuit breaker reliability, and data drift monitoring.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus instrumentation
if settings.enable_metrics:
    Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        excluded_handlers=["/metrics", "/health"],
    ).instrument(app).expose(app, endpoint="/metrics")

# Routes
app.include_router(router, prefix="/api/v1")


# Root redirect to docs
@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health",
    }
