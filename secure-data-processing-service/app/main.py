from __future__ import annotations

from fastapi import FastAPI

from app.api.routes_audit import router as audit_router
from app.api.routes_auth import router as auth_router
from app.api.routes_records import router as record_router
from app.config import settings
from app.database import fetch_one, init_db
from app.security.auth import create_user
from app.security.secrets import LocalSecretsManager
from app.services.audit import AuditService


def create_app() -> FastAPI:
    init_db()
    secrets = LocalSecretsManager()
    AuditService()
    if not fetch_one("SELECT * FROM users WHERE username = ?", (settings.default_admin_username,)):
        create_user(settings.default_admin_username, settings.default_admin_password, "admin", settings.default_admin_org)
        create_user("processor_north", "Processor123!", "processor", "north")
        create_user("analyst_north", "Analyst123!", "analyst", "north")
        create_user("auditor_global", "Auditor123!", "auditor", "root")
    app = FastAPI(title="Secure Data Processing Service", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment, "secrets_provider": settings.secrets_provider, "kms_provider": settings.kms_provider}

    @app.get("/ready")
    def ready() -> dict[str, str]:
        return {"status": "ready", "db": "ok", "db_password_configured": "yes" if secrets.get_secret("db_password") else "no"}

    app.include_router(auth_router)
    app.include_router(record_router)
    app.include_router(audit_router)
    return app


app = create_app()
