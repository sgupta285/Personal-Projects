from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_summary():
    return {
        "sync_endpoints": ["/v1/requests/sync", "/v1/requests/{id}"],
        "async_endpoints": ["/v1/requests/async"],
        "status": "ok",
    }
