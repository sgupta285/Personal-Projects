from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


import httpx


async def main() -> None:
    payload = {
        "user_id": "user_0005",
        "surface": "home",
        "limit": 12,
        "context": {"hour_of_day": 20, "device_type": "ios"},
    }
    latencies = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        for _ in range(25):
            start = time.perf_counter()
            response = await client.post("http://localhost:8000/v1/recommendations/home", json=payload)
            response.raise_for_status()
            latencies.append(time.perf_counter() - start)
    result = {
        "requests": len(latencies),
        "avg_ms": round(sum(latencies) / len(latencies) * 1000, 2),
        "p95_ms": round(sorted(latencies)[int(0.95 * len(latencies)) - 1] * 1000, 2),
    }
    Path("artifacts/benchmarks").mkdir(parents=True, exist_ok=True)
    Path("artifacts/benchmarks/api_benchmark.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
