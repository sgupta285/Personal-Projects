from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, jobs, requests, system
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.database import Base, engine
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_context import RequestContextMiddleware
from app.observability.metrics import MetricsMiddleware, metrics_app

settings = get_settings()
configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Real-Time Service Platform",
    version="1.0.0",
    description="Production-style FastAPI service with tracing, rate limiting, and circuit breaking.",
    lifespan=lifespan,
)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
app.include_router(requests.router, prefix="/v1/requests", tags=["requests"])
app.include_router(jobs.router, prefix="/v1/jobs", tags=["jobs"])
app.include_router(system.router, prefix="/v1/system", tags=["system"])
app.mount("/metrics", metrics_app)


@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "environment": settings.environment,
        "docs": "/docs",
        "metrics": "/metrics",
    }
