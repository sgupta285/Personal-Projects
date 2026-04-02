from __future__ import annotations

import json
import statistics
import time
from collections import Counter, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class MetricsCollector:
    latency_ms: deque[float] = field(default_factory=lambda: deque(maxlen=20_000))
    counters: Counter = field(default_factory=Counter)
    queue_depth_by_partition: dict[int, int] = field(default_factory=dict)

    def incr(self, key: str, value: int = 1) -> None:
        self.counters[key] += value

    def observe_latency(self, ms: float) -> None:
        self.latency_ms.append(ms)

    def set_partition_depths(self, depths: dict[int, int]) -> None:
        self.queue_depth_by_partition = dict(depths)

    def snapshot(self) -> dict[str, Any]:
        latencies = list(self.latency_ms)
        p95 = 0.0
        mean = 0.0
        if latencies:
            mean = statistics.fmean(latencies)
            ordered = sorted(latencies)
            idx = max(0, min(len(ordered) - 1, int(len(ordered) * 0.95) - 1))
            p95 = ordered[idx]
        return {
            "accepted_events": self.counters["accepted_events"],
            "duplicates_skipped": self.counters["duplicates_skipped"],
            "processed_events": self.counters["processed_events"],
            "failed_events": self.counters["failed_events"],
            "dlq_events": self.counters["dlq_events"],
            "retries": self.counters["retries"],
            "mean_latency_ms": round(mean, 2),
            "p95_latency_ms": round(p95, 2),
            "queue_depth_by_partition": self.queue_depth_by_partition,
        }

    def emit_cloudwatch_style_log(self, path: Path) -> None:
        payload = {
            "_aws": {
                "timestamp": int(time.time() * 1000),
                "CloudWatchMetrics": [
                    {
                        "Namespace": "RTDP",
                        "Dimensions": [["service"]],
                        "Metrics": [
                            {"Name": "accepted_events", "Unit": "Count"},
                            {"Name": "processed_events", "Unit": "Count"},
                            {"Name": "dlq_events", "Unit": "Count"},
                            {"Name": "p95_latency_ms", "Unit": "Milliseconds"},
                        ],
                    }
                ],
            },
            "service": "real-time-data-processing-platform",
            **self.snapshot(),
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2))
