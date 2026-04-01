from fastapi import APIRouter, HTTPException, Request

from app.schemas.prediction import BatchPredictionRequest, BatchPredictionResponse, ModelInfoResponse, PredictionRequest, PredictionResponse

router = APIRouter()


@router.get("/health/live")
async def live() -> dict:
    return {"status": "ok"}


@router.get("/health/ready")
async def ready(request: Request) -> dict:
    model_repo = request.app.state.model_repo
    return {"status": "ready" if model_repo.is_ready() else "degraded", "model_ready": model_repo.is_ready()}


@router.post("/v1/predict", response_model=PredictionResponse)
async def predict(payload: PredictionRequest, request: Request) -> PredictionResponse:
    service = request.app.state.prediction_service
    try:
        return await service.predict(payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/v1/batch/predict", response_model=BatchPredictionResponse)
async def batch_predict(payload: BatchPredictionRequest, request: Request) -> BatchPredictionResponse:
    service = request.app.state.prediction_service
    try:
        return await service.predict_batch(payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/v1/model/info", response_model=ModelInfoResponse)
async def model_info(request: Request) -> ModelInfoResponse:
    service = request.app.state.prediction_service
    return service.model_info()


@router.post("/v1/cache/clear")
async def clear_cache(request: Request) -> dict:
    service = request.app.state.prediction_service
    return await service.clear_cache()
