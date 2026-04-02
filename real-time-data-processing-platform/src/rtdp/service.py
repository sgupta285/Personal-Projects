from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .autoscaler import AutoscalerAdvisor
from .broker import PartitionedBroker
from .config import Settings
from .metrics import MetricsCollector
from .storage import Storage
from .worker import StreamWorker, WorkerConfig


@dataclass(slots=True)
class ServiceState:
    settings: Settings
    storage: Storage
    broker: PartitionedBroker
    metrics: MetricsCollector
    autoscaler: AutoscalerAdvisor
    workers: list[StreamWorker]
    worker_tasks: list[asyncio.Task]


class RealtimeProcessingService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.settings.ensure_dirs()
        self.storage = Storage(self.settings.db_path)
        self.broker = PartitionedBroker(self.settings.partitions, self.settings.max_queue_size)
        self.metrics = MetricsCollector()
        self.autoscaler = AutoscalerAdvisor(self.settings.target_latency_ms)
        self.workers: list[StreamWorker] = []
        self.worker_tasks: list[asyncio.Task] = []

    async def start(self) -> None:
        if self.worker_tasks:
            return
        worker_total = max(1, min(self.settings.worker_count, self.settings.partitions))
        partition_groups = [[] for _ in range(worker_total)]
        for partition in range(self.settings.partitions):
            partition_groups[partition % worker_total].append(partition)
        for idx, partitions in enumerate(partition_groups):
            worker = StreamWorker(
                broker=self.broker,
                storage=self.storage,
                metrics=self.metrics,
                config=WorkerConfig(
                    worker_id=idx,
                    partitions=partitions,
                    batch_size=self.settings.batch_size,
                    max_retries=self.settings.max_retries,
                    poll_interval_ms=self.settings.poll_interval_ms,
                ),
            )
            self.workers.append(worker)
            self.worker_tasks.append(asyncio.create_task(worker.run(), name=f"worker-{idx}"))

    async def shutdown(self) -> None:
        for worker in self.workers:
            worker.stop()
        if self.worker_tasks:
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        self.worker_tasks = []
        self.workers = []

    async def ingest(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        accepted = 0
        duplicates = 0
        partitions: list[int] = []
        for event in events:
            if self.storage.is_duplicate(event["idempotency_key"]):
                duplicates += 1
                self.metrics.incr("duplicates_skipped")
                continue
            message = await self.broker.publish(event)
            accepted += 1
            partitions.append(message.partition)
            self.metrics.incr("accepted_events")
        self.metrics.set_partition_depths(self.broker.depths())
        return {
            "accepted": accepted,
            "duplicates": duplicates,
            "queued_partitions": partitions,
        }

    async def replay_dlq(self, dlq_id: str) -> dict[str, Any] | None:
        record = self.storage.get_dlq(dlq_id)
        if not record:
            return None
        event = json.loads(record["body_json"])
        event["failure_mode"] = "none"
        message = await self.broker.publish(event)
        self.storage.mark_dlq_replayed(dlq_id)
        self.metrics.incr("accepted_events")
        return {"replayed": True, "dlq_id": dlq_id, "target_partition": message.partition}

    def status(self) -> dict[str, Any]:
        depths = self.broker.depths()
        self.metrics.set_partition_depths(depths)
        snapshot = self.metrics.snapshot()
        autoscaler = self.autoscaler.recommend(
            queue_depth=self.broker.total_depth(),
            p95_latency_ms=float(snapshot["p95_latency_ms"]),
            current_workers=max(1, len(self.workers) or self.settings.partitions),
        )
        return {
            "queue_depth": self.broker.total_depth(),
            "partitions": depths,
            "metrics": snapshot,
            "autoscaler": autoscaler,
        }

    def emit_metrics_artifact(self, path: Path) -> None:
        self.metrics.emit_cloudwatch_style_log(path)
