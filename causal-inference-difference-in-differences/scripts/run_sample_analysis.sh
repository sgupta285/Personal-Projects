#!/usr/bin/env bash
set -euo pipefail
python -m did_lab.cli --config configs/default.yaml generate-sample
python -m did_lab.cli --config configs/default.yaml run-analysis
