from __future__ import annotations

import json

from redis import Redis

from app.config import get_settings

QUEUE_NAME = "browser-agent:runs"


def get_redis() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)


def enqueue_run(run_id: int) -> None:
    redis_client = get_redis()
    redis_client.rpush(QUEUE_NAME, json.dumps({"run_id": run_id}))


def dequeue_run(timeout_seconds: int = 1) -> int | None:
    redis_client = get_redis()
    item = redis_client.blpop(QUEUE_NAME, timeout=timeout_seconds)
    if not item:
        return None
    _, payload = item
    data = json.loads(payload)
    return int(data["run_id"])
