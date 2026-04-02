import time
from contextlib import asynccontextmanager
from uuid import uuid4
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, ORJSONResponse
from app.api.routes.health import router as health_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.v1_orders import router as v1_orders_router
from app.api.routes.v2_orders import router as v2_orders_router
from app.core.config import get_settings
from app.db import init_db
from app.services.metrics import record_request


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title='Production Service API Platform',
        version='1.0.0',
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
        description='Versioned API platform with API keys, OAuth-style bearer tokens, service tokens, quotas, docs, and operational hooks.',
    )

    @app.middleware('http')
    async def observability_middleware(request: Request, call_next):
        request_id = request.headers.get('X-Request-ID', str(uuid4()))
        request.state.request_id = request_id
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:
            duration = time.perf_counter() - started
            record_request(request.url.path, request.method, 500, duration)
            payload = {
                'error': {
                    'code': 'internal_error',
                    'message': 'An unexpected error occurred',
                    'request_id': request_id,
                }
            }
            return JSONResponse(status_code=500, content=payload)
        duration = time.perf_counter() - started
        client_id = getattr(getattr(request.state, 'auth', None), 'client_id', None)
        record_request(request.url.path, request.method, response.status_code, duration, client_id=client_id)
        response.headers['X-Request-ID'] = request_id
        return response

    @app.exception_handler(Exception)
    async def catch_all(_: Request, exc: Exception):
        return JSONResponse(status_code=500, content={'error': {'code': 'internal_error', 'message': str(exc)}})

    @app.exception_handler(ValueError)
    async def value_error(_: Request, exc: ValueError):
        return JSONResponse(status_code=400, content={'error': {'code': 'invalid_request', 'message': str(exc)}})
    app.include_router(health_router)
    app.include_router(metrics_router)
    app.include_router(v1_orders_router)
    app.include_router(v2_orders_router)

    @app.get('/')
    def root() -> dict[str, str]:
        return {
            'service': settings.app_name,
            'docs': '/docs',
            'openapi': '/openapi.json',
        }

    return app
