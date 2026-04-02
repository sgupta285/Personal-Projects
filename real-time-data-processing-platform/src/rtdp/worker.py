from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any

from .broker import BrokerMessage, PartitionedBroker
from .metrics import MetricsCollector
from .storage import Storage


class TransientProcessingError(RuntimeError):
    pass


class PermanentProcessingError(RuntimeError):
    pass


@dataclass(slots=True)
class WorkerConfig:
    worker_id: int
    partitions: list[int]
    batch_size: int
    max_retries: int
    poll_interval_ms: int


class StreamWorker:
    def __init__(self, broker: PartitionedBroker, storage: Storage, metrics: MetricsCollector, config: WorkerConfig) -> None:
        self.broker = broker
        self.storage = storage
        self.metrics = metrics
        self.config = config
        self.running = False

    async def run(self) -> None:
        self.running = True
        while self.running:
            any_work = False
            for partition in self.config.partitions:
                batch = await self.broker.consume_batch(
                    partition,
                    batch_size=self.config.batch_size,
                    poll_timeout=self.config.poll_interval_ms / 1000,
                )
                if not batch:
                    continue
                any_work = True
                for message in batch:
                    await self.handle(message)
            self.metrics.set_partition_depths(self.broker.depths())
            if not any_work:
                await asyncio.sleep(self.config.poll_interval_ms / 1000)

    def stop(self) -> None:
        self.running = False

    async def handle(self, message: BrokerMessage) -> None:
        event = message.body
        if self.storage.is_duplicate(event["idempotency_key"]):
            self.metrics.incr("duplicates_skipped")
            return
        try:
            start = time.perf_counter()
            await asyncio.sleep(0)
            self._apply_business_logic(event, message)
            latency_ms = (time.perf_counter() - start) * 1000
            stored = self.storage.mark_processed(event, latency_ms)
            if not stored:
                self.metrics.incr("duplicates_skipped")
                return
            self.metrics.incr("processed_events")
            self.metrics.observe_latency(latency_ms)
        except TransientProcessingError as exc:
            self.metrics.incr("retries")
            message.attempts += 1
            if message.attempts >= self.config.max_retries:
                self._send_to_dlq(event, message, str(exc))
                return
            await asyncio.sleep(0.01)
            self.broker.requeue(message)
        except PermanentProcessingError as exc:
            self._send_to_dlq(event, message, str(exc))

    def _apply_business_logic(self, event: dict[str, Any], message: BrokerMessage) -> None:
        mode = event.get("failure_mode", "none")
        if mode == "transient_once" and message.attempts == 0:
            raise TransientProcessingError("transient failure on first attempt")
        if mode == "always":
            raise PermanentProcessingError("permanent processing failure")

    def _send_to_dlq(self, event: dict[str, Any], message: BrokerMessage, error: str) -> None:
        dlq_id = f"dlq_{event['event_id']}"
        self.storage.add_dlq(dlq_id, event, message.attempts + 1, error)
        self.metrics.incr("failed_events")
        self.metrics.incr("dlq_events")
