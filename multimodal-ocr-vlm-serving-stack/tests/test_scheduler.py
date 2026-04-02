from app.models.schemas import DocumentInput, JobRecord, JobType
from app.services.scheduler import MemoryAwareScheduler


def test_scheduler_respects_budget() -> None:
    scheduler = MemoryAwareScheduler(gpu_memory_budget_mb=150)
    jobs = [
        JobRecord(job_type=JobType.VLM, payload={'items': [DocumentInput(document_id='a', image_width=4096, image_height=4096, page_count=1).model_dump()]}),
        JobRecord(job_type=JobType.VLM, payload={'items': [DocumentInput(document_id='b', image_width=800, image_height=600, page_count=1).model_dump()]}),
    ]
    decision = scheduler.choose(jobs)
    assert decision.estimated_memory_mb <= 150
    assert len(decision.items) >= 1
    assert len(decision.items) + len(decision.deferred) == 2
