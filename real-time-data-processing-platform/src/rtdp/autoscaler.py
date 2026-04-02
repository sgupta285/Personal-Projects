from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AutoscalerAdvisor:
    target_latency_ms: int
    max_workers: int = 12

    def recommend(self, queue_depth: int, p95_latency_ms: float, current_workers: int) -> dict[str, int | float | str]:
        desired = current_workers
        reason = "steady"
        if queue_depth > current_workers * 200 or p95_latency_ms > self.target_latency_ms:
            desired = min(self.max_workers, current_workers + max(1, queue_depth // 300))
            reason = "backlog_or_latency_pressure"
        elif queue_depth < max(5, current_workers * 20) and current_workers > 1 and p95_latency_ms < self.target_latency_ms * 0.5:
            desired = max(1, current_workers - 1)
            reason = "low_backlog"
        return {
            "current_workers": current_workers,
            "desired_workers": desired,
            "queue_depth": queue_depth,
            "p95_latency_ms": round(p95_latency_ms, 2),
            "reason": reason,
        }
