from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class LatencyEvent:
    timestamp: str
    release: str
    event_type: str
    duration_us: float
    cpu: int
    pid: int
    tid: int
    comm: str
    syscall: str | None = None
    irq: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SummaryStats:
    count: int
    mean_us: float
    p50_us: float
    p95_us: float
    p99_us: float
    max_us: float


@dataclass(slots=True)
class RegressionFinding:
    event_type: str
    baseline_p99_us: float
    candidate_p99_us: float
    delta_pct: float
    severity: str
    note: str
