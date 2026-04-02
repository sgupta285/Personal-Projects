from __future__ import annotations

import os
from pathlib import Path
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "secure-data-processing-service")
    environment: str = os.getenv("ENVIRONMENT", "local")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./secure_service.db")
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me-in-production-super-secret-32b")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_ttl_minutes: int = int(os.getenv("ACCESS_TOKEN_TTL_MINUTES", "30"))
    mfa_issuer: str = os.getenv("MFA_ISSUER", "Secure Data Processing Service")
    kms_provider: str = os.getenv("KMS_PROVIDER", "local")
    local_kms_key_path: Path = Path(os.getenv("LOCAL_KMS_KEY_PATH", "./artifacts/local_kms_key.json"))
    secrets_provider: str = os.getenv("SECRETS_PROVIDER", "local")
    local_secrets_file: Path = Path(os.getenv("LOCAL_SECRETS_FILE", "./artifacts/local_secrets.json"))
    audit_log_path: Path = Path(os.getenv("AUDIT_LOG_PATH", "./artifacts/audit_chain.jsonl"))
    default_admin_username: str = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    default_admin_password: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "ChangeMe123!")
    default_admin_org: str = os.getenv("DEFAULT_ADMIN_ORG", "root")


settings = Settings()
