#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="$(pwd)/tools/fwtool"
python -m fwtool.cli build --version "${1:-0.1.0}"
python -m fwtool.cli package --version "${1:-0.1.0}"
release_path=$(ls dist/firmware-demo-board-"${1:-0.1.0}".tar.gz)
python -m fwtool.cli verify "$release_path"
python -m fwtool.cli hil --version "${1:-0.1.0}" --port 9120
