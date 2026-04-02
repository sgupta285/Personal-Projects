from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from .config import Settings
from .schemas import DLQRecord, EventBatchIn, EventIn, IngestResponse, ReplayResponse, StatusResponse
from .service import RealtimeProcessingService

settings = Settings()
service = RealtimeProcessingService(settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await service.start()
    yield
    await service.shutdown()


app = FastAPI(title="Real-Time Data Processing Platform", version="0.1.0", lifespan=lifespan)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/events", response_model=IngestResponse)
async def ingest_event(payload: EventIn | EventBatchIn):
    events = payload.events if isinstance(payload, EventBatchIn) else [payload]
    result = await service.ingest([event.model_dump(mode="json") for event in events])
    return IngestResponse(**result)


@app.get("/v1/status", response_model=StatusResponse)
async def status() -> StatusResponse:
    return StatusResponse(**service.status())


@app.get("/v1/entities")
async def list_entities():
    return {"items": service.storage.list_entities()}


@app.get("/v1/entities/{entity_id}")
async def get_entity(entity_id: str):
    entity = service.storage.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="entity not found")
    return entity


@app.get("/v1/dlq", response_model=list[DLQRecord])
async def list_dlq() -> list[DLQRecord]:
    records = []
    for row in service.storage.list_dlq():
        records.append(
            DLQRecord(
                dlq_id=row["dlq_id"],
                event_id=row["event_id"],
                entity_id=row["entity_id"],
                attempts=row["attempts"],
                last_error=row["last_error"],
                created_at=row["created_at"],
            )
        )
    return records


@app.post("/v1/dlq/replay/{dlq_id}", response_model=ReplayResponse)
async def replay(dlq_id: str) -> ReplayResponse:
    result = await service.replay_dlq(dlq_id)
    if not result:
        raise HTTPException(status_code=404, detail="dlq record not found")
    return ReplayResponse(**result)
