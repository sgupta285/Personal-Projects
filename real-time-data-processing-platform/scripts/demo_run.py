from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path

from rtdp.config import Settings
from rtdp.service import RealtimeProcessingService


async def main() -> None:
    settings = Settings()
    service = RealtimeProcessingService(settings)
    await service.start()
    now = datetime.now(timezone.utc).isoformat()
    events = [
        {
            "event_id": "evt_demo_1",
            "entity_id": "acct_100",
            "event_type": "purchase",
            "occurred_at": now,
            "payload": {"amount": 49.99, "currency": "USD"},
            "idempotency_key": "acct_100-purchase-evt_demo_1",
            "failure_mode": "none",
        },
        {
            "event_id": "evt_demo_2",
            "entity_id": "acct_100",
            "event_type": "purchase",
            "occurred_at": now,
            "payload": {"amount": 59.99, "currency": "USD"},
            "idempotency_key": "acct_100-purchase-evt_demo_2",
            "failure_mode": "transient_once",
        },
        {
            "event_id": "evt_demo_3",
            "entity_id": "acct_999",
            "event_type": "purchase",
            "occurred_at": now,
            "payload": {"amount": 79.99, "currency": "USD"},
            "idempotency_key": "acct_999-purchase-evt_demo_3",
            "failure_mode": "always",
        },
    ]
    await service.ingest(events)
    await asyncio.sleep(0.4)
    status = service.status()
    print("Status after demo run:")
    print(status)
    service.emit_metrics_artifact(Path("artifacts/cloudwatch_metrics.json"))
    await service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
