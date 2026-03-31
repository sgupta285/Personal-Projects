#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${API_BASE_URL:-http://localhost:8080}"

RUN_ID=$(curl -s -X POST "$API_BASE_URL/runs" \
  -H 'Content-Type: application/json' \
  -d @data/sample-run-request.json | python -c 'import json,sys; print(json.load(sys.stdin)["data"]["id"])')

echo "Created run: $RUN_ID"

echo "Executing run..."
curl -s -X POST "$API_BASE_URL/runs/$RUN_ID/execute" \
  -H 'Content-Type: application/json' \
  -d '{}'

echo
echo "Run detail:"
curl -s "$API_BASE_URL/runs/$RUN_ID"
