from __future__ import annotations

import asyncio
import logging
import time

from app.config import get_settings
from app.db import SessionLocal
from app.services.queue import dequeue_run
from app.services.tasks import get_run
from app.runtime.executor import TaskExecutor
from app.utils.logging import configure_logging

configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


async def process_run(run_id: int) -> None:
    db = SessionLocal()
    try:
        run = get_run(db, run_id)
        if not run:
            logger.warning("Run %s not found", run_id)
            return
        executor = TaskExecutor()
        await executor.execute_run(db, run)
        logger.info("Processed run %s with status %s", run.id, run.status.value)
    finally:
        db.close()


def main() -> None:
    logger.info("Worker started")
    while True:
        run_id = dequeue_run(timeout_seconds=settings.worker_poll_interval)
        if run_id is None:
            continue
        asyncio.run(process_run(run_id))


if __name__ == "__main__":
    main()
