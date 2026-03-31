
from __future__ import annotations

import logging
import time

from app.core.config import settings
from app.db.base import Base
from app.models import Document, DocumentRevision, ParseJob  # noqa: F401
from app.db.session import SessionLocal, engine
from app.services.jobs import next_queued_job, process_job

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main() -> None:
    settings.ensure_dirs()
    Base.metadata.create_all(bind=engine)
    logging.info("worker started")
    while True:
        session = SessionLocal()
        try:
            job = next_queued_job(session)
            if job is None:
                time.sleep(settings.worker_poll_seconds)
                continue
            logging.info("processing job %s for document %s", job.id, job.document_id)
            process_job(session, job)
        finally:
            session.close()
        time.sleep(0.1)


if __name__ == "__main__":
    main()
