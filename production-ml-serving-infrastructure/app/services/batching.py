import asyncio
from dataclasses import dataclass

from app.core.config import settings
from app.schemas.prediction import FeaturePayload
from app.services.metrics import BATCH_SIZE_HISTOGRAM, INFERENCE_LATENCY


@dataclass
class BatchItem:
    payload: FeaturePayload
    future: asyncio.Future


class DynamicBatcher:
    def __init__(self, model_repo):
        self.model_repo = model_repo
        self.queue: asyncio.Queue[BatchItem] = asyncio.Queue()
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def infer(self, payload: FeaturePayload) -> float:
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        await self.queue.put(BatchItem(payload=payload, future=future))
        return await future

    async def _run(self) -> None:
        while self._running:
            item = await self.queue.get()
            batch = [item]
            await asyncio.sleep(settings.request_batch_window_ms / 1000.0)
            while len(batch) < settings.request_max_batch_size and not self.queue.empty():
                batch.append(self.queue.get_nowait())
            BATCH_SIZE_HISTOGRAM.observe(len(batch))
            with INFERENCE_LATENCY.labels(model_kind="active").time():
                scores = self.model_repo.predict_scores([entry.payload for entry in batch])
            for entry, score in zip(batch, scores, strict=True):
                if not entry.future.done():
                    entry.future.set_result(score)
