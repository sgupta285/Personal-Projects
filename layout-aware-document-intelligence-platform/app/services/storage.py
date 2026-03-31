
from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.utils.files import safe_filename


def persist_upload(upload: UploadFile) -> Path:
    suffix = Path(upload.filename or "document.bin").suffix
    stem = Path(upload.filename or "document").stem
    target_name = f"{stem}-{uuid.uuid4().hex[:10]}{suffix}"
    target_path = settings.upload_dir / safe_filename(target_name)
    with target_path.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)
    return target_path


def artifact_directory(document_id: str, version: int) -> Path:
    path = settings.artifact_dir / document_id / f"v{version}"
    path.mkdir(parents=True, exist_ok=True)
    return path
