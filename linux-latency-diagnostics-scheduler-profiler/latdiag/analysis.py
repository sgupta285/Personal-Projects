from __future__ import annotations

import math
from collections import defaultdict
from statistics import mean

from .models import LatencyEvent, RegressionFinding, SummaryStats


def summarize(events: list[LatencyEvent], group_by: str = "event_type") -> dict[str, SummaryStats]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for event in events:
        key = getattr(event, group_by)
        grouped[str(key)].append(event.duration_us)
    return {key: _stats(values) for key, values in grouped.items()}


def top_cpu_hotspots(events: list[LatencyEvent], limit: int = 10) -> list[dict[str, float | int | str]]:
    totals: dict[tuple[int, str], list[float]] = defaultdict(list)
    for event in events:
        totals[(event.cpu, event.comm)].append(event.duration_us)
    ranked = sorted(
        (
            {
                "cpu": cpu,
                "comm": comm,
                "samples": len(values),
                "total_us": round(sum(values), 2),
                "p99_us": round(_percentile(values, 99), 2),
            }
            for (cpu, comm), values in totals.items()
        ),
        key=lambda row: (row["p99_us"], row["total_us"]),
        reverse=True,
    )
    return ranked[:limit]


def syscall_tail(events: list[LatencyEvent], limit: int = 10) -> list[dict[str, float | int | str]]:
    totals: dict[str, list[float]] = defaultdict(list)
    for event in events:
        if event.syscall:
            totals[event.syscall].append(event.duration_us)
    ranked = sorted(
        (
            {
                "syscall": name,
                "samples": len(values),
                "mean_us": round(mean(values), 2),
                "p99_us": round(_percentile(values, 99), 2),
            }
            for name, values in totals.items()
        ),
        key=lambda row: (row["p99_us"], row["mean_us"]),
        reverse=True,
    )
    return ranked[:limit]


def compare_releases(
    baseline: list[LatencyEvent],
    candidate: list[LatencyEvent],
    threshold_pct: float = 15.0,
) -> list[RegressionFinding]:
    base_summary = summarize(baseline)
    cand_summary = summarize(candidate)
    findings: list[RegressionFinding] = []
    for event_type, base_stats in base_summary.items():
        if event_type not in cand_summary:
            continue
        cand_stats = cand_summary[event_type]
        if base_stats.p99_us == 0:
            continue
        delta_pct = ((cand_stats.p99_us - base_stats.p99_us) / base_stats.p99_us) * 100.0
        if delta_pct < threshold_pct:
            continue
        severity = "critical" if delta_pct >= 40 else "warning"
        note = _interpret_regression(event_type, delta_pct)
        findings.append(
            RegressionFinding(
                event_type=event_type,
                baseline_p99_us=round(base_stats.p99_us, 2),
                candidate_p99_us=round(cand_stats.p99_us, 2),
                delta_pct=round(delta_pct, 2),
                severity=severity,
                note=note,
            )
        )
    findings.sort(key=lambda finding: finding.delta_pct, reverse=True)
    return findings


def scheduler_delay_breakdown(events: list[LatencyEvent]) -> list[dict[str, float | str | int]]:
    by_comm: dict[str, list[float]] = defaultdict(list)
    for event in events:
        if event.event_type == "scheduler_delay":
            by_comm[event.comm].append(event.duration_us)
    return sorted(
        (
            {
                "comm": comm,
                "samples": len(values),
                "mean_us": round(mean(values), 2),
                "p95_us": round(_percentile(values, 95), 2),
                "p99_us": round(_percentile(values, 99), 2),
            }
            for comm, values in by_comm.items()
        ),
        key=lambda row: row["p99_us"],
        reverse=True,
    )


def _stats(values: list[float]) -> SummaryStats:
    ordered = sorted(values)
    return SummaryStats(
        count=len(ordered),
        mean_us=round(mean(ordered), 2),
        p50_us=round(_percentile(ordered, 50), 2),
        p95_us=round(_percentile(ordered, 95), 2),
        p99_us=round(_percentile(ordered, 99), 2),
        max_us=round(max(ordered), 2),
    )


def _percentile(values: list[float], percentile: int) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    rank = (len(ordered) - 1) * (percentile / 100)
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return ordered[int(rank)]
    weight = rank - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def _interpret_regression(event_type: str, delta_pct: float) -> str:
    if event_type == "scheduler_delay":
        return f"Scheduler wait tail increased by {delta_pct:.1f}%. Check CPU affinity, runnable queue pressure, and noisy neighbors."
    if event_type == "syscall_latency":
        return f"Syscall tail increased by {delta_pct:.1f}%. Inspect storage or network interrupts and perf hotspots."
    if event_type == "interrupt":
        return f"Interrupt service time increased by {delta_pct:.1f}%. Review IRQ balancing and hardware driver changes."
    return f"Latency tail increased by {delta_pct:.1f}%. Compare release traces and isolate CPU hot spots."
