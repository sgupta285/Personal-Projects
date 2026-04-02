from typing import Any

from app.repositories.usage_repository import UsageRepository
from app.services.cache import cache_service
from app.services.metrics import CACHE_HITS, CACHE_MISSES


class AnalyticsService:
    def __init__(self, repository: UsageRepository) -> None:
        self.repository = repository

    def get_summary(self, workspace_id: str, start_date, end_date, interval: str) -> dict[str, Any]:
        payload = {
            "workspace_id": workspace_id,
            "start_date": start_date,
            "end_date": end_date,
            "interval": interval,
        }
        key = cache_service.build_key("summary", payload)
        cached = cache_service.get_json(key)
        if cached:
            CACHE_HITS.labels("summary").inc()
            return cached
        CACHE_MISSES.labels("summary").inc()
        result = self.repository.fetch_summary(workspace_id, start_date, end_date, interval)
        cache_service.set_json(key, result)
        return result

    def get_breakdown(self, workspace_id: str, start_date, end_date, interval: str, dimension: str, limit: int) -> dict[str, Any]:
        payload = {
            "workspace_id": workspace_id,
            "start_date": start_date,
            "end_date": end_date,
            "interval": interval,
            "dimension": dimension,
            "limit": limit,
        }
        key = cache_service.build_key("breakdown", payload)
        cached = cache_service.get_json(key)
        if cached:
            CACHE_HITS.labels("breakdown").inc()
            return cached
        CACHE_MISSES.labels("breakdown").inc()
        result = self.repository.fetch_breakdown(workspace_id, start_date, end_date, interval, dimension, limit)
        cache_service.set_json(key, result)
        return result

    def get_metric_catalog(self) -> dict[str, Any]:
        payload = {"kind": "catalog"}
        key = cache_service.build_key("catalog", payload)
        cached = cache_service.get_json(key)
        if cached:
            CACHE_HITS.labels("catalog").inc()
            return cached
        CACHE_MISSES.labels("catalog").inc()
        result = self.repository.build_metric_catalog()
        cache_service.set_json(key, result)
        return result
