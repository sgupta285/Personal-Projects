#!/usr/bin/env bash
# Pull the raw NYC Parks Properties export used by prepare_data.py.
# Source: NYC Open Data, dataset enfh-gkve.
set -euo pipefail
mkdir -p data
curl -sS --max-time 90 \
  "https://data.cityofnewyork.us/resource/enfh-gkve.json?%24limit=3000" \
  -o data/parks_raw.json
echo "Saved data/parks_raw.json"
