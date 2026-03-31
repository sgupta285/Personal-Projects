
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Layout-Aware Document Intelligence Platform")
    environment: str = os.getenv("ENVIRONMENT", "development")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
    data_dir: Path = Path(os.getenv("DATA_DIR", "./data"))
    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", "./data/uploads"))
    artifact_dir: Path = Path(os.getenv("ARTIFACT_DIR", "./data/artifacts"))
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "50"))
    worker_poll_seconds: float = float(os.getenv("WORKER_POLL_SECONDS", "2"))
    schema_version: str = os.getenv("SCHEMA_VERSION", "1.0.0")
    enable_ocr_fallback: bool = os.getenv("ENABLE_OCR_FALLBACK", "true").lower() == "true"
    tesseract_cmd: str = os.getenv("TESSERACT_CMD", "tesseract")

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.artifact_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
