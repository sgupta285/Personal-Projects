from __future__ import annotations

from app.core.config import settings
from app.services.cache import MemoryCache
from app.services.job_store import JobStore
from app.services.queue import InMemoryQueue
from app.services.workers import WorkerOrchestrator

queue = InMemoryQueue()
store = JobStore(settings.job_storage_path)
cache = MemoryCache(ttl_seconds=settings.cache_ttl_seconds)
orchestrator = WorkerOrchestrator(queue=queue, store=store, cache=cache)
