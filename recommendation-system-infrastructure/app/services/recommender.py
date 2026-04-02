from __future__ import annotations

from app.models.schemas import RecommendationItem, RecommendationRequest, RecommendationResponse
from app.services.ab_testing import ExperimentService
from app.services.cache import TTLCache
from app.services.candidate_generation import CandidateGenerator
from app.services.feature_store import FeatureStore
from app.services.ranking import RankingService


class RecommendationService:
    def __init__(self, cache: TTLCache, ab_testing: ExperimentService, feature_store: FeatureStore, candidate_generator: CandidateGenerator, ranking_service: RankingService) -> None:
        self.cache = cache
        self.ab_testing = ab_testing
        self.feature_store = feature_store
        self.candidate_generator = candidate_generator
        self.ranking_service = ranking_service

    def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        cache_key = self.cache.build_key(request.model_dump())
        cached = self.cache.get(cache_key)
        if cached:
            return RecommendationResponse(**cached)

        assignment = self.ab_testing.get_assignment(request.user_id)
        variant = assignment["variant"]

        if request.surface == "related_items" and request.item_id:
            candidates = self.candidate_generator.similar_items(request.item_id, top_k=max(request.limit * 10, 50))
        else:
            candidates = self.candidate_generator.for_user(request.user_id, top_k=max(request.limit * 10, 50))

        ranked = self.ranking_service.rerank(request.user_id, candidates, request.context.model_dump(), variant=variant)
        items = []
        for row in ranked[: request.limit]:
            metadata = self.feature_store.get_item_features(row["item_id"])
            reason = self._reason(metadata, row["features"], variant)
            items.append(RecommendationItem(
                item_id=row["item_id"],
                title=metadata.get("title", row["item_id"]),
                category=metadata.get("category", "unknown"),
                score=round(row["score"], 4),
                reason=reason,
                experiment_variant=variant,
                features=row["features"],
            ))

        response = RecommendationResponse(
            user_id=request.user_id,
            surface=request.surface,
            variant=variant,
            candidates_considered=len(candidates),
            items=items,
        )
        self.cache.set(cache_key, response.model_dump())
        return response

    @staticmethod
    def _reason(metadata: dict, features: dict, variant: str) -> str:
        if features.get("category_match"):
            return f"Strong category match in {metadata.get('category', 'this category')} with {variant} ranking"
        return f"Trending item boosted by popularity and context features in {variant} ranking"
