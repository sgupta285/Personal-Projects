from fastapi import FastAPI

from app.api.routes import router
from app.config import settings
from app.db import init_db

init_db()

app = FastAPI(title=settings.app_name)
app.include_router(router, prefix=settings.api_prefix)
