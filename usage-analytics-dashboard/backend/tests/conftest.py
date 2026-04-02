from pathlib import Path

from app.db.base import Base
from app.db.session import engine
from app.models import UsageEvent, UsageRollup
from app.repositories.usage_repository import UsageRepository
from app.db.session import SessionLocal
from scripts.seed_usage_data import generate_rows, load_database, write_csv
from scripts.refresh_rollups import refresh_rollups


def pytest_sessionstart(session):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        has_events = db.query(UsageEvent).first() is not None
        has_rollups = db.query(UsageRollup).first() is not None
    if not has_events:
        rows = generate_rows()
        write_csv(rows)
        load_database(rows)
    if not has_rollups:
        refresh_rollups()
