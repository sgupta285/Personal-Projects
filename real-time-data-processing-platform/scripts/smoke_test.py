from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from rtdp.config import Settings
from rtdp.service import RealtimeProcessingService


async def main() -> None:
    settings = Settings()
    service = RealtimeProcessingService(settings)
    await service.start()
    now = datetime.now(timezone.utc).isoformat()
    events = [
        {
            "event_id": "evt_smoke_ok",
            "entity_id": "acct_smoke_1",
            "event_type": "purchase",
            "occurred_at": now,
            "payload": {"amount": 10},
            "idempotency_key": "acct_smoke_1-purchase-ok",
            "failure_mode": "none",
        },
        {
            "event_id": "evt_smoke_ok_dup",
            "entity_id": "acct_smoke_1",
            "event_type": "purchase",
            "occurred_at": now,
            "payload": {"amount": 10},
            "idempotency_key": "acct_smoke_1-purchase-ok",
            "failure_mode": "none",
        },
        {
            "event_id": "evt_smoke_retry",
            "entity_id": "acct_smoke_2",
            "event_type": "purchase",
            "occurred_at": now,
            "payload": {"amount": 22},
            "idempotency_key": "acct_smoke_2-purchase-retry",
            "failure_mode": "transient_once",
        },
        {
            "event_id": "evt_smoke_dlq",
            "entity_id": "acct_smoke_3",
            "event_type": "purchase",
            "occurred_at": now,
            "payload": {"amount": 33},
            "idempotency_key": "acct_smoke_3-purchase-dlq",
            "failure_mode": "always",
        },
    ]
    result = await service.ingest(events)
    assert result["accepted"] == 4
    await asyncio.sleep(0.5)
    status = service.status()
    assert status["metrics"]["processed_events"] >= 2
    dlq = service.storage.list_dlq()
    assert dlq, "expected at least one DLQ record"
    replayed = await service.replay_dlq(dlq[0]["dlq_id"])
    assert replayed is not None
    await asyncio.sleep(0.2)
    final = service.status()
    print("Smoke test passed")
    print(final)
    await service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
