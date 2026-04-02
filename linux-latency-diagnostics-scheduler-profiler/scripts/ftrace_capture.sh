#!/usr/bin/env bash
set -euo pipefail
OUT_DIR="${1:-artifacts/raw/ftrace}"
TRACE_ROOT="/sys/kernel/debug/tracing"
mkdir -p "$OUT_DIR"
if [[ ! -d "$TRACE_ROOT" ]]; then
  echo "ftrace debugfs not available. Run on a Linux host with tracing enabled."
  exit 0
fi
sudo sh -c "echo nop > $TRACE_ROOT/current_tracer"
sudo sh -c "echo 1 > $TRACE_ROOT/events/sched/sched_switch/enable"
sudo sh -c "echo 1 > $TRACE_ROOT/events/irq/irq_handler_entry/enable"
sleep 1
sudo cat "$TRACE_ROOT/trace" > "$OUT_DIR/trace.txt"
sudo sh -c "echo 0 > $TRACE_ROOT/events/sched/sched_switch/enable"
sudo sh -c "echo 0 > $TRACE_ROOT/events/irq/irq_handler_entry/enable"
echo "ftrace trace written to $OUT_DIR/trace.txt"
