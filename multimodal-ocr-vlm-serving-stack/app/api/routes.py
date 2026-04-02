from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.api.deps import queue, store
from app.core.config import settings
from app.core.metrics import JOB_SUBMISSIONS
from app.models.schemas import HealthResponse, JobAccepted, JobList, JobRecord, JobStatus, JobType, OcrRequest, PipelineRequest, VlmRequest

router = APIRouter()


@router.get('/healthz', response_model=HealthResponse)
async def healthz() -> HealthResponse:
    return HealthResponse(status='ok', queue_depth=queue.size(), gpu_memory_budget_mb=settings.gpu_memory_budget_mb)


@router.get('/jobs', response_model=JobList)
async def list_jobs() -> JobList:
    return JobList(jobs=store.list())


@router.get('/jobs/{job_id}', response_model=JobRecord)
async def get_job(job_id: str) -> JobRecord:
    job = store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail='job_not_found')
    return job


@router.post('/ocr', response_model=JobAccepted)
async def submit_ocr(request: OcrRequest) -> JobAccepted:
    job = JobRecord(job_type=JobType.OCR, payload=request.model_dump())
    store.save(job)
    await queue.put(job)
    JOB_SUBMISSIONS.labels(job_type='ocr').inc()
    return JobAccepted(job_id=job.job_id, status=JobStatus.QUEUED)


@router.post('/vlm', response_model=JobAccepted)
async def submit_vlm(request: VlmRequest) -> JobAccepted:
    job = JobRecord(job_type=JobType.VLM, payload=request.model_dump())
    store.save(job)
    await queue.put(job)
    JOB_SUBMISSIONS.labels(job_type='vlm').inc()
    return JobAccepted(job_id=job.job_id, status=JobStatus.QUEUED)


@router.post('/pipeline', response_model=JobAccepted)
async def submit_pipeline(request: PipelineRequest) -> JobAccepted:
    job = JobRecord(job_type=JobType.PIPELINE, payload=request.model_dump())
    store.save(job)
    await queue.put(job)
    JOB_SUBMISSIONS.labels(job_type='pipeline').inc()
    return JobAccepted(job_id=job.job_id, status=JobStatus.QUEUED)
