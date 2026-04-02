#!/usr/bin/env bash
set -euo pipefail
OUT_DIR="${1:-artifacts/raw}"
mkdir -p "$OUT_DIR"
perf stat -x, -e context-switches,cpu-migrations,minor-faults,major-faults sleep 1 2> "$OUT_DIR/perf_stat.csv" || true
perf sched record -- sleep 1 >/dev/null 2>&1 || true
perf sched latency > "$OUT_DIR/perf_sched_latency.txt" 2>/dev/null || true
printf 'raw perf artifacts written to %s\n' "$OUT_DIR"
