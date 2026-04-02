from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    db_path: Path = Path(os.getenv("RTDP_DB_PATH", "./data/rtdp.db"))
    partitions: int = int(os.getenv("RTDP_PARTITIONS", "6"))
    max_queue_size: int = int(os.getenv("RTDP_MAX_QUEUE_SIZE", "5000"))
    max_retries: int = int(os.getenv("RTDP_MAX_RETRIES", "3"))
    batch_size: int = int(os.getenv("RTDP_BATCH_SIZE", "32"))
    worker_count: int = int(os.getenv("RTDP_WORKER_COUNT", "3"))
    target_latency_ms: int = int(os.getenv("RTDP_TARGET_LATENCY_MS", "500"))
    poll_interval_ms: int = int(os.getenv("RTDP_POLL_INTERVAL_MS", "20"))

    def ensure_dirs(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
