from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.services.metrics import metrics_middleware, metrics_response

app = FastAPI(title="Usage Analytics Dashboard API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(metrics_middleware)
app.include_router(router)
app.add_api_route("/metrics", metrics_response, methods=["GET"])
