from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path

import pytest

from rtdp.config import Settings
from rtdp.service import RealtimeProcessingService


@pytest.mark.asyncio
async def test_duplicate_is_processed_once(tmp_path: Path):
    service = RealtimeProcessingService(Settings(db_path=tmp_path / "rtdp.db"))
    await service.start()
    now = datetime.now(timezone.utc).isoformat()
    event = {
        "event_id": "evt_1",
        "entity_id": "acct_1",
        "event_type": "purchase",
        "occurred_at": now,
        "payload": {"amount": 25},
        "idempotency_key": "acct_1-evt_1",
        "failure_mode": "none",
    }
    await service.ingest([event, dict(event)])
    await asyncio.sleep(0.2)
    entity = service.storage.get_entity("acct_1")
    assert entity is not None
    assert entity["event_count"] == 1
    status = service.status()
    assert status["metrics"]["duplicates_skipped"] >= 1
    await service.shutdown()


@pytest.mark.asyncio
async def test_permanent_failure_goes_to_dlq(tmp_path: Path):
    service = RealtimeProcessingService(Settings(db_path=tmp_path / "rtdp.db", max_retries=2))
    await service.start()
    now = datetime.now(timezone.utc).isoformat()
    event = {
        "event_id": "evt_fail",
        "entity_id": "acct_fail",
        "event_type": "purchase",
        "occurred_at": now,
        "payload": {"amount": 25},
        "idempotency_key": "acct_fail-evt_fail",
        "failure_mode": "always",
    }
    await service.ingest([event])
    await asyncio.sleep(0.2)
    dlq = service.storage.list_dlq()
    assert len(dlq) == 1
    assert dlq[0]["event_id"] == "evt_fail"
    await service.shutdown()
