from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class BrokerMessage:
    partition: int
    offset: int
    body: dict[str, Any]
    attempts: int = 0


class PartitionedBroker:
    def __init__(self, partitions: int, max_queue_size: int = 5000) -> None:
        self.partitions = partitions
        self.queues = [asyncio.Queue(maxsize=max_queue_size) for _ in range(partitions)]
        self.offsets = [0 for _ in range(partitions)]

    def choose_partition(self, entity_id: str) -> int:
        digest = hashlib.sha256(entity_id.encode("utf-8")).hexdigest()
        return int(digest, 16) % self.partitions

    async def publish(self, body: dict[str, Any]) -> BrokerMessage:
        partition = self.choose_partition(body["entity_id"])
        offset = self.offsets[partition]
        self.offsets[partition] += 1
        message = BrokerMessage(partition=partition, offset=offset, body=body)
        await self.queues[partition].put(message)
        return message

    async def consume_batch(self, partition: int, batch_size: int, poll_timeout: float) -> list[BrokerMessage]:
        items: list[BrokerMessage] = []
        try:
            first = await asyncio.wait_for(self.queues[partition].get(), timeout=poll_timeout)
            items.append(first)
        except TimeoutError:
            return items
        while len(items) < batch_size:
            try:
                items.append(self.queues[partition].get_nowait())
            except asyncio.QueueEmpty:
                break
        return items

    def requeue(self, message: BrokerMessage) -> None:
        self.queues[message.partition].put_nowait(message)

    def depths(self) -> dict[int, int]:
        return {idx: q.qsize() for idx, q in enumerate(self.queues)}

    def total_depth(self) -> int:
        return sum(q.qsize() for q in self.queues)
