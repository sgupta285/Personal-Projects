from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import typer

from .analysis import compare_releases, scheduler_delay_breakdown, summarize, syscall_tail, top_cpu_hotspots
from .collect import capture_snapshot, save_metadata
from .io import read_events
from .reporting.html import write_report

app = typer.Typer(help="Linux latency diagnostics and scheduler profiling toolkit")


@app.command()
def capture(
    output: Path = typer.Option(..., help="Output capture file (.jsonl)"),
    release: str = typer.Option("local", help="Release label for the capture"),
    sample: bool = typer.Option(False, help="Use built-in sample data instead of host collectors"),
) -> None:
    capture_snapshot(output=output, release=release, use_sample=sample)
    save_metadata(output.parent, {"release": release, "sample": sample})
    typer.echo(f"Wrote capture to {output}")


@app.command()
def summarize_capture(
    capture_file: Path = typer.Argument(..., exists=True),
    output: Path | None = typer.Option(None, help="Optional JSON output path"),
) -> None:
    events = read_events(capture_file)
    payload = {key: asdict(value) for key, value in summarize(events).items()}
    if output:
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        typer.echo(f"Summary written to {output}")
        return
    typer.echo(json.dumps(payload, indent=2))


@app.command()
def compare(
    baseline: Path = typer.Argument(..., exists=True),
    candidate: Path = typer.Argument(..., exists=True),
    output_dir: Path = typer.Option(Path("artifacts/report"), help="Directory for JSON and HTML output"),
    threshold_pct: float = typer.Option(15.0, help="Percent increase required to flag a regression"),
) -> None:
    baseline_events = read_events(baseline)
    candidate_events = read_events(candidate)
    payload = {
        "baseline": {key: asdict(value) for key, value in summarize(baseline_events).items()},
        "candidate": {key: asdict(value) for key, value in summarize(candidate_events).items()},
        "regressions": [asdict(item) for item in compare_releases(baseline_events, candidate_events, threshold_pct=threshold_pct)],
        "hotspots": top_cpu_hotspots(candidate_events),
        "syscalls": syscall_tail(candidate_events),
        "scheduler": scheduler_delay_breakdown(candidate_events),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "comparison.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    html_path = write_report(payload, output_dir / "comparison.html")
    typer.echo(f"Comparison JSON written to {json_path}")
    typer.echo(f"HTML report written to {html_path}")


@app.command()
def demo(output_dir: Path = typer.Option(Path("artifacts/demo"), help="Where to place demo outputs")) -> None:
    baseline = output_dir / "baseline.jsonl"
    candidate = output_dir / "candidate.jsonl"
    capture_snapshot(baseline, release="v1.1.0", use_sample=True)
    capture_snapshot(candidate, release="v1.2.0", use_sample=True)
    # overwrite candidate with heavier synthetic tail
    candidate.write_text("\n".join([
        json.dumps({"timestamp":"2026-04-02T17:00:00Z","release":"v1.2.0","event_type":"scheduler_delay","duration_us":240.0,"cpu":2,"pid":911,"tid":911,"comm":"worker-a","syscall":None,"irq":None,"metadata":{"source":"synthetic"}}),
        json.dumps({"timestamp":"2026-04-02T17:00:01Z","release":"v1.2.0","event_type":"scheduler_delay","duration_us":310.0,"cpu":2,"pid":912,"tid":912,"comm":"worker-a","syscall":None,"irq":None,"metadata":{"source":"synthetic"}}),
        json.dumps({"timestamp":"2026-04-02T17:00:02Z","release":"v1.2.0","event_type":"syscall_latency","duration_us":190.0,"cpu":2,"pid":913,"tid":913,"comm":"gateway","syscall":"epoll_wait","irq":None,"metadata":{"source":"synthetic"}}),
        json.dumps({"timestamp":"2026-04-02T17:00:03Z","release":"v1.2.0","event_type":"interrupt","duration_us":115.0,"cpu":3,"pid":0,"tid":0,"comm":"irq/eth0","syscall":None,"irq":"eth0-TxRx","metadata":{"source":"synthetic"}})
    ]) + "\n", encoding="utf-8")
    compare(baseline, candidate, output_dir=output_dir / "report", threshold_pct=10.0)
