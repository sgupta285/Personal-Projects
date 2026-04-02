from __future__ import annotations

import asyncio
import logging

from app.core.config import settings
from app.core.metrics import JOB_COMPLETIONS, JOB_LATENCY
from app.models.schemas import DocumentInput, JobRecord, JobStatus, JobType
from app.services.cache import MemoryCache
from app.services.job_store import JobStore
from app.services.ocr import MockOcrEngine
from app.services.pipeline import PipelineService
from app.services.queue import InMemoryQueue
from app.services.scheduler import MemoryAwareScheduler
from app.services.vlm import MockVlmEngine

logger = logging.getLogger(__name__)


class WorkerOrchestrator:
    def __init__(self, queue: InMemoryQueue, store: JobStore, cache: MemoryCache):
        self.queue = queue
        self.store = store
        self.cache = cache
        self.scheduler = MemoryAwareScheduler(settings.gpu_memory_budget_mb)
        self.ocr = MockOcrEngine()
        self.vlm = MockVlmEngine()
        self.pipeline = PipelineService()
        self._tasks: list[asyncio.Task] = []
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        for job_type in (JobType.OCR, JobType.VLM, JobType.PIPELINE):
            for worker_idx in range(max(1, settings.gpu_worker_count)):
                task = asyncio.create_task(self._loop(job_type), name=f"worker-{job_type.value}-{worker_idx}")
                self._tasks.append(task)

    async def stop(self) -> None:
        self._stop_event.set()
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        self._stop_event = asyncio.Event()

    async def _loop(self, job_type: JobType) -> None:
        while not self._stop_event.is_set():
            try:
                batch = await self.queue.get_batch(job_type, settings.max_batch_size, settings.batch_wait_ms)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.exception("worker_loop_error job_type=%s error=%s", job_type, exc)
                await asyncio.sleep(0.1)
                continue
            decision = self.scheduler.choose(batch)
            for deferred in decision.deferred:
                await self.queue.put(deferred)
            await self._process(decision.items)

    async def _process(self, jobs: list[JobRecord]) -> None:
        for job in jobs:
            self.store.mark_status(job.job_id, JobStatus.RUNNING)
            start = asyncio.get_running_loop().time()
            try:
                result = await asyncio.to_thread(self._run_job, job)
                self.store.mark_status(job.job_id, JobStatus.COMPLETED, result=result)
                JOB_COMPLETIONS.labels(job_type=job.job_type.value, status='completed').inc()
            except Exception as exc:
                self.store.mark_status(job.job_id, JobStatus.FAILED, error=str(exc))
                JOB_COMPLETIONS.labels(job_type=job.job_type.value, status='failed').inc()
            finally:
                duration = asyncio.get_running_loop().time() - start
                JOB_LATENCY.labels(job_type=job.job_type.value).observe(duration)

    def _run_job(self, job: JobRecord) -> dict:
        cache_key = self.cache.make_key(job.job_type.value, job.payload)
        cached = self.cache.get(cache_key)
        if cached is not None:
            return {**cached, 'cache': 'hit'}
        items = [DocumentInput.model_validate(item) for item in job.payload.get('items', [])]
        if job.job_type == JobType.OCR:
            result = self.ocr.run(items, language=job.payload.get('language', 'en'), use_layout=job.payload.get('use_layout', True))
        elif job.job_type == JobType.VLM:
            result = self.vlm.run(items, prompt=job.payload.get('prompt', 'Summarize this image'), max_tokens=job.payload.get('max_tokens', 128))
        else:
            result = self.pipeline.run(items, prompt=job.payload.get('prompt', ''), language=job.payload.get('language', 'en'))
        self.cache.set(cache_key, result)
        return {**result, 'cache': 'miss'}
