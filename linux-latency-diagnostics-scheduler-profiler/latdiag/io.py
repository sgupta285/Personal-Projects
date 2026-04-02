from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from .models import LatencyEvent


def read_events(path: str | Path) -> list[LatencyEvent]:
    file_path = Path(path)
    if file_path.suffix == ".jsonl":
        return _read_jsonl(file_path)
    if file_path.suffix == ".csv":
        return _read_csv(file_path)
    raise ValueError(f"Unsupported capture format: {file_path}")


def write_events(events: Iterable[LatencyEvent], path: str | Path) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as handle:
        for event in events:
            row = {
                "timestamp": event.timestamp,
                "release": event.release,
                "event_type": event.event_type,
                "duration_us": event.duration_us,
                "cpu": event.cpu,
                "pid": event.pid,
                "tid": event.tid,
                "comm": event.comm,
                "syscall": event.syscall,
                "irq": event.irq,
                "metadata": event.metadata,
            }
            handle.write(json.dumps(row) + "\n")


def _read_jsonl(file_path: Path) -> list[LatencyEvent]:
    events: list[LatencyEvent] = []
    with file_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            events.append(_row_to_event(row))
    return events


def _read_csv(file_path: Path) -> list[LatencyEvent]:
    events: list[LatencyEvent] = []
    with file_path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            metadata_raw = row.get("metadata") or "{}"
            row = dict(row)
            row["metadata"] = json.loads(metadata_raw)
            events.append(_row_to_event(row))
    return events


def _row_to_event(row: dict) -> LatencyEvent:
    return LatencyEvent(
        timestamp=str(row["timestamp"]),
        release=str(row.get("release", "unknown")),
        event_type=str(row["event_type"]),
        duration_us=float(row["duration_us"]),
        cpu=int(row.get("cpu", 0)),
        pid=int(row.get("pid", 0)),
        tid=int(row.get("tid", row.get("pid", 0))),
        comm=str(row.get("comm", "unknown")),
        syscall=row.get("syscall"),
        irq=row.get("irq"),
        metadata=dict(row.get("metadata") or {}),
    )
