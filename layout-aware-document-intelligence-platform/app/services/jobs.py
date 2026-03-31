
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document, DocumentRevision, ParseJob
from app.schemas.document import DocumentParseResult
from app.services.comparison import summarize_result
from app.services.parser import DocumentParser
from app.services.storage import artifact_directory


def enqueue_parse_job(session: Session, document: Document, requested_by: str | None = None) -> ParseJob:
    job = ParseJob(document_id=document.id, status="queued", requested_by=requested_by)
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def next_queued_job(session: Session) -> ParseJob | None:
    stmt = select(ParseJob).where(ParseJob.status == "queued").order_by(ParseJob.created_at.asc())
    return session.execute(stmt).scalars().first()


def process_job(session: Session, job: ParseJob) -> ParseJob:
    document = session.get(Document, job.document_id)
    if document is None:
        job.status = "failed"
        job.error_message = "Document not found."
        session.commit()
        return job

    try:
        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        session.commit()

        latest_version = max((revision.version for revision in document.revisions), default=0)
        target_version = latest_version + 1
        artifact_dir = artifact_directory(document.id, target_version)

        parser = DocumentParser()
        result_model: DocumentParseResult = parser.parse(
            path=document.storage_path,
            filename=document.filename,
            content_type=document.content_type,
            artifact_dir=artifact_dir,
        )
        result_json = result_model.model_dump(mode="json")
        summary = summarize_result(result_json)

        revision = DocumentRevision(
            document_id=document.id,
            version=target_version,
            schema_version=settings.schema_version,
            result_json=result_json,
            summary_json=summary,
        )
        session.add(revision)

        job.status = "completed"
        job.completed_at = datetime.now(timezone.utc)
        job.error_message = None
        session.commit()
        session.refresh(job)
        return job
    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)
        job.completed_at = datetime.now(timezone.utc)
        session.commit()
        session.refresh(job)
        return job
