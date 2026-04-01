import argparse
import asyncio
import json
import statistics
from pathlib import Path
from time import perf_counter

import httpx


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = int(round((len(ordered) - 1) * pct))
    return ordered[idx]


def build_payload(index: int) -> dict:
    return {
        "request_id": f"bench-{index}",
        "features": {
            "account_tenure_days": 50 + (index % 400),
            "avg_session_seconds": 120 + (index % 900),
            "prior_purchases": index % 12,
            "cart_additions_7d": index % 15,
            "email_click_rate": round((index % 100) / 100, 2),
            "discount_sensitivity": 0.35 + ((index % 40) / 100),
            "inventory_score": 0.50 + ((index % 30) / 100),
            "device_trust_score": 0.65 + ((index % 20) / 100),
        },
    }


async def worker(client: httpx.AsyncClient, sem: asyncio.Semaphore, index: int, latencies: list[float], errors: list[int]) -> None:
    async with sem:
        payload = build_payload(index)
        start = perf_counter()
        response = await client.post("http://localhost:8000/v1/predict", json=payload)
        latencies.append(perf_counter() - start)
        if response.status_code >= 400:
            errors.append(index)


async def main(requests: int, concurrency: int) -> dict:
    latencies: list[float] = []
    errors: list[int] = []
    sem = asyncio.Semaphore(concurrency)
    start = perf_counter()
    async with httpx.AsyncClient(timeout=10.0) as client:
        await asyncio.gather(*(worker(client, sem, i, latencies, errors) for i in range(requests)))
    elapsed = perf_counter() - start
    result = {
        "requests": requests,
        "concurrency": concurrency,
        "throughput_rps": round(requests / elapsed, 2),
        "avg_latency_ms": round(statistics.mean(latencies) * 1000, 2),
        "p50_latency_ms": round(percentile(latencies, 0.50) * 1000, 2),
        "p95_latency_ms": round(percentile(latencies, 0.95) * 1000, 2),
        "p99_latency_ms": round(percentile(latencies, 0.99) * 1000, 2),
        "errors": len(errors),
    }
    output_dir = Path("artifacts/benchmarks")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"benchmark_{requests}_{concurrency}.json"
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=10)
    args = parser.parse_args()
    asyncio.run(main(args.requests, args.concurrency))
