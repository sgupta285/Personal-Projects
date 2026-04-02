from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from rtdp.config import Settings
from rtdp.service import RealtimeProcessingService


async def main(events: int, concurrency: int) -> None:
    settings = Settings()
    service = RealtimeProcessingService(settings)
    await service.start()
    now = datetime.now(timezone.utc).isoformat()

    async def send_chunk(start_idx: int, end_idx: int) -> None:
        batch = []
        for idx in range(start_idx, end_idx):
            batch.append(
                {
                    "event_id": f"evt_bench_{idx}",
                    "entity_id": f"acct_{idx % 200}",
                    "event_type": "purchase",
                    "occurred_at": now,
                    "payload": {"amount": float((idx % 90) + 10)},
                    "idempotency_key": f"acct_{idx % 200}-evt_bench_{idx}",
                    "failure_mode": "none",
                }
            )
        await service.ingest(batch)

    start = time.perf_counter()
    chunk_size = max(1, events // concurrency)
    tasks = []
    for idx in range(concurrency):
        lo = idx * chunk_size
        hi = events if idx == concurrency - 1 else min(events, (idx + 1) * chunk_size)
        tasks.append(asyncio.create_task(send_chunk(lo, hi)))
    await asyncio.gather(*tasks)
    max_wait_seconds = 10.0
    while True:
        if service.status()["queue_depth"] == 0:
            break
        if time.perf_counter() - start > max_wait_seconds:
            break
        await asyncio.sleep(0.05)
    elapsed = time.perf_counter() - start
    status = service.status()
    snapshot = status["metrics"]
    latencies = [snapshot["mean_latency_ms"], snapshot["p95_latency_ms"]]
    result = {
        "events_requested": events,
        "accepted_events": snapshot["accepted_events"],
        "processed_events": snapshot["processed_events"],
        "duplicates_skipped": snapshot["duplicates_skipped"],
        "dlq_events": snapshot["dlq_events"],
        "throughput_events_per_sec": round(snapshot["processed_events"] / elapsed, 2) if elapsed else 0.0,
        "mean_latency_ms": snapshot["mean_latency_ms"],
        "p95_latency_ms": snapshot["p95_latency_ms"],
        "queue_depth": status["queue_depth"],
        "autoscaler": status["autoscaler"],
        "latency_summary_ms": {
            "mean_of_summary_points": round(statistics.fmean(latencies), 2),
        },
    }
    out = Path("artifacts/benchmark_results.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    await service.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=int, default=1500)
    parser.add_argument("--concurrency", type=int, default=8)
    args = parser.parse_args()
    asyncio.run(main(args.events, args.concurrency))
