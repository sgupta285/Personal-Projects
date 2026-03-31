
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.models.document import Document, DocumentRevision, ParseJob
from app.schemas.document import (
    DocumentResponse,
    JobResponse,
    RevisionCompareResponse,
    RevisionResponse,
    UploadResponse,
)
from app.services.comparison import compare_revisions
from app.services.jobs import enqueue_parse_job
from app.services.storage import persist_upload
from app.utils.files import guess_content_type
from app.utils.hashing import sha256_file

router = APIRouter()


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/documents/upload", response_model=UploadResponse)
def upload_document(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> UploadResponse:
    stored_path = persist_upload(file)
    content_type = file.content_type or guess_content_type(file.filename or stored_path.name)
    document = Document(
        filename=file.filename or stored_path.name,
        content_type=content_type,
        size_bytes=stored_path.stat().st_size,
        sha256=sha256_file(stored_path),
        storage_path=str(stored_path),
    )
    session.add(document)
    session.commit()
    session.refresh(document)

    job = enqueue_parse_job(session, document)
    return UploadResponse(document_id=document.id, job_id=job.id, status=job.status)


@router.get("/documents", response_model=list[DocumentResponse])
def list_documents(session: Session = Depends(get_session)) -> list[DocumentResponse]:
    documents = session.execute(select(Document).order_by(Document.created_at.desc())).scalars().all()
    responses: list[DocumentResponse] = []
    for document in documents:
        latest_version = max((revision.version for revision in document.revisions), default=None)
        responses.append(
            DocumentResponse(
                id=document.id,
                filename=document.filename,
                content_type=document.content_type,
                size_bytes=document.size_bytes,
                sha256=document.sha256,
                created_at=document.created_at,
                latest_version=latest_version,
            )
        )
    return responses


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, session: Session = Depends(get_session)) -> DocumentResponse:
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    latest_version = max((revision.version for revision in document.revisions), default=None)
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        content_type=document.content_type,
        size_bytes=document.size_bytes,
        sha256=document.sha256,
        created_at=document.created_at,
        latest_version=latest_version,
    )


@router.post("/documents/{document_id}/parse", response_model=UploadResponse)
def reparse_document(document_id: str, session: Session = Depends(get_session)) -> UploadResponse:
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    job = enqueue_parse_job(session, document)
    return UploadResponse(document_id=document.id, job_id=job.id, status=job.status)


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str, session: Session = Depends(get_session)) -> JobResponse:
    job = session.get(ParseJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return JobResponse(
        id=job.id,
        document_id=job.document_id,
        status=job.status,
        error_message=job.error_message,
        requested_by=job.requested_by,
        started_at=job.started_at,
        completed_at=job.completed_at,
        created_at=job.created_at,
    )


@router.get("/documents/{document_id}/revisions", response_model=list[RevisionResponse])
def list_revisions(document_id: str, session: Session = Depends(get_session)) -> list[RevisionResponse]:
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return [
        RevisionResponse(
            id=revision.id,
            document_id=revision.document_id,
            version=revision.version,
            schema_version=revision.schema_version,
            summary_json=revision.summary_json,
            created_at=revision.created_at,
        )
        for revision in document.revisions
    ]


@router.get("/documents/{document_id}/revisions/{version}")
def get_revision(document_id: str, version: int, session: Session = Depends(get_session)) -> dict:
    stmt = (
        select(DocumentRevision)
        .where(DocumentRevision.document_id == document_id, DocumentRevision.version == version)
        .limit(1)
    )
    revision = session.execute(stmt).scalars().first()
    if revision is None:
        raise HTTPException(status_code=404, detail="Revision not found.")
    return revision.result_json


@router.get("/documents/{document_id}/compare/latest", response_model=RevisionCompareResponse)
def compare_latest_revisions(document_id: str, session: Session = Depends(get_session)) -> RevisionCompareResponse:
    revisions = (
        session.execute(
            select(DocumentRevision)
            .where(DocumentRevision.document_id == document_id)
            .order_by(DocumentRevision.version.asc())
        )
        .scalars()
        .all()
    )
    if len(revisions) < 2:
        raise HTTPException(status_code=400, detail="At least two revisions are required for comparison.")

    left = revisions[-2]
    right = revisions[-1]
    changes = compare_revisions(left.result_json, right.result_json)
    return RevisionCompareResponse(
        document_id=document_id,
        from_version=left.version,
        to_version=right.version,
        changes=changes,
    )
