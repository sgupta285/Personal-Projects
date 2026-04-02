from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from .io import write_events
from .models import LatencyEvent


SAMPLE_EVENTS = [
    LatencyEvent(datetime.now(UTC).isoformat(), "sample", "scheduler_delay", 120.0, 1, 412, 412, "worker-a", metadata={"source": "synthetic"}),
    LatencyEvent(datetime.now(UTC).isoformat(), "sample", "syscall_latency", 92.0, 1, 512, 512, "worker-a", syscall="epoll_wait", metadata={"source": "synthetic"}),
    LatencyEvent(datetime.now(UTC).isoformat(), "sample", "interrupt", 48.0, 3, 0, 0, "irq/eth0", irq="eth0-TxRx", metadata={"source": "synthetic"}),
]


def capture_snapshot(output: str | Path, release: str, use_sample: bool = False) -> Path:
    output_path = Path(output)
    if use_sample:
        events = [
            LatencyEvent(
                timestamp=event.timestamp,
                release=release,
                event_type=event.event_type,
                duration_us=event.duration_us,
                cpu=event.cpu,
                pid=event.pid,
                tid=event.tid,
                comm=event.comm,
                syscall=event.syscall,
                irq=event.irq,
                metadata=dict(event.metadata),
            )
            for event in SAMPLE_EVENTS
        ]
        write_events(events, output_path)
        return output_path

    events: list[LatencyEvent] = []
    timestamp = datetime.now(UTC).isoformat()
    try:
        proc = subprocess.run(
            ["bash", "-lc", "perf stat -x, -e context-switches,cpu-migrations,minor-faults,major-faults sleep 0.2"],
            check=False,
            capture_output=True,
            text=True,
        )
        stderr = proc.stderr.strip()
        for line in stderr.splitlines():
            parts = [part.strip() for part in line.split(",")]
            if len(parts) < 3:
                continue
            value_text, _, metric = parts[:3]
            try:
                value = float(value_text.replace("<not counted>", "0").replace("<not supported>", "0") or 0)
            except ValueError:
                continue
            events.append(
                LatencyEvent(
                    timestamp=timestamp,
                    release=release,
                    event_type="perf_counter",
                    duration_us=value,
                    cpu=0,
                    pid=0,
                    tid=0,
                    comm=metric,
                    metadata={"collector": "perf"},
                )
            )
    except FileNotFoundError:
        pass

    if not events:
        return capture_snapshot(output_path, release=release, use_sample=True)

    write_events(events, output_path)
    return output_path


def save_metadata(output_dir: str | Path, metadata: dict) -> Path:
    path = Path(output_dir) / "capture_metadata.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return path
