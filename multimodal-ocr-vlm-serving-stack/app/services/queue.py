from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any

from app.core.metrics import QUEUE_DEPTH
from app.models.schemas import JobRecord, JobType


class InMemoryQueue:
    def __init__(self):
        self._queues: dict[JobType, asyncio.Queue[JobRecord]] = defaultdict(asyncio.Queue)

    async def put(self, job: JobRecord) -> None:
        await self._queues[job.job_type].put(job)
        self._update_metrics()

    async def get_batch(self, job_type: JobType, max_items: int, wait_ms: int) -> list[JobRecord]:
        queue = self._queues[job_type]
        first = await queue.get()
        batch = [first]
        deadline = asyncio.get_running_loop().time() + (wait_ms / 1000)
        while len(batch) < max_items:
            timeout = deadline - asyncio.get_running_loop().time()
            if timeout <= 0:
                break
            try:
                item = await asyncio.wait_for(queue.get(), timeout=timeout)
                batch.append(item)
            except asyncio.TimeoutError:
                break
        self._update_metrics()
        return batch

    def size(self) -> int:
        return sum(q.qsize() for q in self._queues.values())

    def _update_metrics(self) -> None:
        QUEUE_DEPTH.set(self.size())
