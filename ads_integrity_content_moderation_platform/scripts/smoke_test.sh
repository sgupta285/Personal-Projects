#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000/api/v1}"

curl --fail "${BASE_URL}/analytics/overview" >/dev/null
echo "API is reachable."

python scripts/seed_ads.py
sleep 3

echo "Overview:"
curl --fail "${BASE_URL}/analytics/overview"
echo
