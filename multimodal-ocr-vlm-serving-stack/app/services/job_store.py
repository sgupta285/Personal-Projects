from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from app.models.schemas import JobRecord, JobStatus


class JobStore:
    def __init__(self, path: str):
        self.root = Path(path)
        self.root.mkdir(parents=True, exist_ok=True)

    def _job_path(self, job_id: str) -> Path:
        return self.root / f"{job_id}.json"

    def save(self, job: JobRecord) -> None:
        self._job_path(job.job_id).write_text(job.model_dump_json(indent=2), encoding='utf-8')

    def get(self, job_id: str) -> JobRecord | None:
        path = self._job_path(job_id)
        if not path.exists():
            return None
        return JobRecord.model_validate_json(path.read_text(encoding='utf-8'))

    def list(self) -> list[JobRecord]:
        jobs = []
        for path in sorted(self.root.glob('*.json')):
            jobs.append(JobRecord.model_validate_json(path.read_text(encoding='utf-8')))
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        return jobs

    def mark_status(self, job_id: str, status: JobStatus, result: dict | None = None, error: str | None = None) -> JobRecord:
        job = self.get(job_id)
        if job is None:
            raise KeyError(job_id)
        job.status = status
        job.result = result
        job.error = error
        from app.models.schemas import utcnow
        job.updated_at = utcnow()
        self.save(job)
        return job
