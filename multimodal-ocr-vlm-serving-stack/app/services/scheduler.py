from __future__ import annotations

from dataclasses import dataclass

from app.core.metrics import BATCH_SIZE, GPU_MEMORY_USED
from app.models.schemas import DocumentInput, JobRecord, JobType


@dataclass
class BatchDecision:
    items: list[JobRecord]
    deferred: list[JobRecord]
    estimated_memory_mb: int


class MemoryAwareScheduler:
    def __init__(self, gpu_memory_budget_mb: int):
        self.gpu_memory_budget_mb = gpu_memory_budget_mb

    @staticmethod
    def estimate_document_memory(item: DocumentInput, mode: JobType) -> int:
        pixels = item.image_width * item.image_height * max(item.page_count, 1)
        base = max(32, pixels // 500000)
        if mode == JobType.VLM:
            return base * 3
        if mode == JobType.PIPELINE:
            return base * 4
        return base

    def choose(self, jobs: list[JobRecord]) -> BatchDecision:
        selected: list[JobRecord] = []
        deferred: list[JobRecord] = []
        total = 0
        for idx, job in enumerate(jobs):
            payload_items = job.payload.get('items', [])
            estimated = sum(self.estimate_document_memory(DocumentInput.model_validate(item), job.job_type) for item in payload_items)
            job.estimated_memory_mb = estimated
            if selected and total + estimated > self.gpu_memory_budget_mb:
                deferred.extend(jobs[idx:])
                break
            if total + estimated > self.gpu_memory_budget_mb:
                selected = [job]
                total = min(estimated, self.gpu_memory_budget_mb)
                deferred.extend(jobs[idx + 1:])
                break
            selected.append(job)
            total += estimated
        if not selected and jobs:
            first = jobs[0]
            first.estimated_memory_mb = min(self.gpu_memory_budget_mb, first.estimated_memory_mb or 128)
            selected = [first]
            total = first.estimated_memory_mb
            deferred = jobs[1:]
        GPU_MEMORY_USED.set(total)
        BATCH_SIZE.observe(len(selected) or 1)
        return BatchDecision(items=selected, deferred=deferred, estimated_memory_mb=total)
