"""
E-Commerce Backend API
FastAPI REST services with PostgreSQL/SQLite, Redis cache-aside, and rate limiting.
"""

import time
import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.database import init_db, close_db
from app.services.redis_service import redis_service
from app.api.products import router as products_router
from app.api.orders import router as orders_router
from app.api.categories_customers import cat_router, cust_router
from app.middleware.rate_limit import RateLimitMiddleware

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()
_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting", app=settings.app_name)
    await init_db()
    redis_service.connect()
    logger.info("startup_complete", db="ready", cache=redis_service.is_available)
    yield
    logger.info("shutting_down")
    redis_service.disconnect()
    await close_db()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="REST API with Redis cache-aside, rate limiting, connection pooling, "
                "and indexed queries. Designed for high-concurrency read-heavy workloads.",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(RateLimitMiddleware)

# Routes
app.include_router(products_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")
app.include_router(cat_router, prefix="/api/v1")
app.include_router(cust_router, prefix="/api/v1")


@app.get("/health", tags=["Operations"])
async def health():
    return {
        "status": "healthy",
        "database": "connected",
        "cache": "connected" if redis_service.is_available else "unavailable",
        "version": settings.app_version,
        "uptime_seconds": round(time.time() - _start_time, 1),
    }


@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/api/v1/cache/stats", tags=["Operations"])
async def cache_stats():
    return redis_service.get_stats()
