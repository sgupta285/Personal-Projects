from __future__ import annotations

from app.core.config import settings
from app.services.ab_testing import ExperimentService
from app.services.cache import TTLCache
from app.services.candidate_generation import CandidateGenerator
from app.services.feature_store import FeatureStore
from app.services.ranking import RankingService
from app.services.recommender import RecommendationService


class Runtime:
    def __init__(self) -> None:
        self.is_loaded = False
        self.cache = TTLCache(ttl_seconds=settings.cache_ttl_seconds)
        self.ab_testing = ExperimentService()
        self.feature_store = FeatureStore()
        self.candidate_generator = CandidateGenerator()
        self.ranking_service = RankingService(self.feature_store)
        self.recommender = RecommendationService(
            cache=self.cache,
            ab_testing=self.ab_testing,
            feature_store=self.feature_store,
            candidate_generator=self.candidate_generator,
            ranking_service=self.ranking_service,
        )

    def load(self) -> None:
        self.feature_store.load()
        self.candidate_generator.load()
        self.ranking_service.load(settings.model_dir_path / "ranking_model.pt")
        self.is_loaded = True


runtime = Runtime()
