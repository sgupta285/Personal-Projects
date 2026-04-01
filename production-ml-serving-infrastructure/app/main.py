from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from prometheus_client import make_asgi_app

from app.api.routes import router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import init_db
from app.services.batching import DynamicBatcher
from app.services.cache import PredictionCache
from app.services.feature_store import FeatureStore
from app.services.model_loader import ModelRepository
from app.services.prediction_service import PredictionService


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    init_db()
    cache = PredictionCache()
    model_repo = ModelRepository()
    feature_store = FeatureStore()
    batcher = DynamicBatcher(model_repo=model_repo)
    await batcher.start()
    service = PredictionService(
        cache=cache,
        model_repo=model_repo,
        feature_store=feature_store,
        batcher=batcher,
    )
    app.state.prediction_service = service
    app.state.cache = cache
    app.state.model_repo = model_repo
    try:
        yield
    finally:
        await batcher.stop()
        await cache.close()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(router)
app.mount("/metrics", make_asgi_app())
