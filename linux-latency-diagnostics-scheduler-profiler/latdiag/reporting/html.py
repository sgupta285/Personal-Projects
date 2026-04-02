from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_report(payload: dict[str, Any], output: str | Path) -> Path:
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    baseline = payload.get("baseline") or {}
    candidate = payload.get("candidate") or {}
    regressions = payload.get("regressions") or []
    hotspots = payload.get("hotspots") or []
    syscalls = payload.get("syscalls") or []
    sched = payload.get("scheduler") or []

    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <title>Latency Diagnostics Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #202124; }}
    h1, h2 {{ margin-bottom: 8px; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 24px; }}
    th, td {{ border: 1px solid #d7d7d7; padding: 8px; text-align: left; }}
    th {{ background: #f5f5f5; }}
    .critical {{ color: #b00020; font-weight: 700; }}
    .warning {{ color: #a15c00; font-weight: 700; }}
    pre {{ background: #f7f7f8; padding: 12px; border-radius: 8px; overflow-x: auto; }}
  </style>
</head>
<body>
  <h1>Linux Latency Diagnostics Report</h1>
  <p>Offline analysis of scheduler delay, syscall latency, and interrupt behavior across releases.</p>
  <h2>Release Summary</h2>
  <pre>{json.dumps({"baseline": baseline, "candidate": candidate}, indent=2)}</pre>
  <h2>Regression Findings</h2>
  {_table(regressions, ["event_type", "baseline_p99_us", "candidate_p99_us", "delta_pct", "severity", "note"]) }
  <h2>CPU Hot Spots</h2>
  {_table(hotspots, ["cpu", "comm", "samples", "total_us", "p99_us"]) }
  <h2>Syscall Tail</h2>
  {_table(syscalls, ["syscall", "samples", "mean_us", "p99_us"]) }
  <h2>Scheduler Delay Breakdown</h2>
  {_table(sched, ["comm", "samples", "mean_us", "p95_us", "p99_us"]) }
</body>
</html>
"""
    output_path.write_text(html, encoding="utf-8")
    return output_path


def _table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "<p>No data available.</p>"
    header = "".join(f"<th>{column}</th>" for column in columns)
    body_rows = []
    for row in rows:
        class_name = str(row.get("severity", ""))
        cells = "".join(f"<td>{row.get(column, '')}</td>" for column in columns)
        body_rows.append(f"<tr class='{class_name}'>{cells}</tr>")
    return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"
