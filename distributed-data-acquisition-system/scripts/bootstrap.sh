#!/usr/bin/env bash
set -euo pipefail

make build
python3 scripts/run_benchmarks.py
python3 scripts/analyze_results.py
