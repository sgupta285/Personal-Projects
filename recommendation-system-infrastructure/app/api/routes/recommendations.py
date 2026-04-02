from fastapi import APIRouter

from app.models.schemas import RecommendationRequest, RecommendationResponse
from app.services.metrics import metrics
from app.services.runtime import runtime

router = APIRouter()


@router.post("/home", response_model=RecommendationResponse)
def home_feed(request: RecommendationRequest) -> RecommendationResponse:
    with metrics.request_timer(request.surface):
        return runtime.recommender.recommend(request)


@router.post("/search", response_model=RecommendationResponse)
def search_results(request: RecommendationRequest) -> RecommendationResponse:
    with metrics.request_timer(request.surface):
        return runtime.recommender.recommend(request)


@router.post("/related", response_model=RecommendationResponse)
def related_items(request: RecommendationRequest) -> RecommendationResponse:
    with metrics.request_timer(request.surface):
        return runtime.recommender.recommend(request)
