#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="$(pwd)/tools/fwtool"
start=$(python - <<'PY'
import time
print(time.time())
PY
)
python -m fwtool.cli build --version "0.2.0" >/tmp/fw_build_1.json
mid=$(python - <<'PY'
import time
print(time.time())
PY
)
python -m fwtool.cli build --version "0.2.0" >/tmp/fw_build_2.json
end=$(python - <<'PY'
import time
print(time.time())
PY
)
python - <<'PY'
import json
from pathlib import Path
first = json.loads(Path('/tmp/fw_build_1.json').read_text())
second = json.loads(Path('/tmp/fw_build_2.json').read_text())
print(json.dumps({
    'first_build_cache_hit': first['cache_hit'],
    'second_build_cache_hit': second['cache_hit'],
}, indent=2))
PY
python - <<PY
start=float("$start")
mid=float("$mid")
end=float("$end")
print(f"first_build_seconds={mid-start:.4f}")
print(f"second_build_seconds={end-mid:.4f}")
PY
