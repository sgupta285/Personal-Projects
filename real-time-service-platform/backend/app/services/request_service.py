import json
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import ServiceRequest, User
from app.services.downstream import process_downstream


class RequestService:
    def __init__(self, db: Session):
        self.db = db

    def create_request(self, user: User, kind: str, payload: dict, priority: int) -> ServiceRequest:
        record = ServiceRequest(
            owner_id=user.id,
            kind=kind,
            payload=json.dumps(payload),
            priority=priority,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def execute_sync(self, record: ServiceRequest, payload: dict) -> ServiceRequest:
        try:
            record.status = "processing"
            self.db.commit()
            latency_ms = process_downstream(payload)
            record.status = "completed"
            record.downstream_latency_ms = latency_ms
            record.error_message = None
        except Exception as exc:
            record.status = "failed"
            record.error_message = str(exc)
            raise
        finally:
            self.db.commit()
            self.db.refresh(record)
        return record

    def enqueue_async(self, background_tasks: BackgroundTasks, record: ServiceRequest, payload: dict) -> None:
        background_tasks.add_task(self._background_execute, record.id, payload)

    def _background_execute(self, request_id: int, payload: dict) -> None:
        db = SessionLocal()
        try:
            record = db.get(ServiceRequest, request_id)
            if record is None:
                return
            try:
                record.status = "processing"
                db.commit()
                latency_ms = process_downstream(payload)
                record.status = "completed"
                record.downstream_latency_ms = latency_ms
                record.error_message = None
            except Exception as exc:
                record.status = "failed"
                record.error_message = str(exc)
            finally:
                db.commit()
        finally:
            db.close()
