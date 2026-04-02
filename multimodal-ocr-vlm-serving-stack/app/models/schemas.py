from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class JobType(str, Enum):
    OCR = "ocr"
    VLM = "vlm"
    PIPELINE = "pipeline"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentInput(BaseModel):
    document_id: str = Field(default_factory=lambda: str(uuid4()))
    text_hint: str | None = None
    image_width: int = 1280
    image_height: int = 720
    page_count: int = 1
    priority: int = 1


class OcrRequest(BaseModel):
    items: list[DocumentInput]
    language: str = "en"
    use_layout: bool = True


class VlmRequest(BaseModel):
    items: list[DocumentInput]
    prompt: str = "Summarize this image"
    max_tokens: int = 128


class PipelineRequest(BaseModel):
    items: list[DocumentInput]
    prompt: str = "Extract key entities and summarize layout"
    language: str = "en"


class JobRecord(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid4()))
    job_type: JobType
    status: JobStatus = JobStatus.QUEUED
    payload: dict[str, Any]
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    estimated_memory_mb: int = 0


class JobAccepted(BaseModel):
    job_id: str
    status: JobStatus


class HealthResponse(BaseModel):
    status: str
    queue_depth: int
    gpu_memory_budget_mb: int


class JobList(BaseModel):
    jobs: list[JobRecord]
