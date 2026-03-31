#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../backend"
uvicorn app.main:app --reload --port 8000
