#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build"
ENGINE_BIN="${BUILD_DIR}/matching_engine_app"
DATA_FILE="${ROOT_DIR}/data/orders.csv"

python3 "${ROOT_DIR}/scripts/generate_orders.py"
cmake -S "${ROOT_DIR}" -B "${BUILD_DIR}" >/dev/null
cmake --build "${BUILD_DIR}" -j >/dev/null

perf record -g -- "${ENGINE_BIN}" "${DATA_FILE}"
perf report --stdio > "${ROOT_DIR}/docs/perf-report.txt"
