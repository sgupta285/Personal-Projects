import asyncio
import statistics
import time

import httpx

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "partner-demo-key"
REQUESTS = 50
CONCURRENCY = 10


async def make_request(client: httpx.AsyncClient) -> float:
    start = time.perf_counter()
    response = await client.get("/api/v1/orders", headers={"X-API-Key": API_KEY})
    response.raise_for_status()
    return time.perf_counter() - start


async def main() -> None:
    semaphore = asyncio.Semaphore(CONCURRENCY)
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        async def wrapped() -> float:
            async with semaphore:
                return await make_request(client)

        latencies = await asyncio.gather(*[wrapped() for _ in range(REQUESTS)])
    p95_index = max(int(len(latencies) * 0.95) - 1, 0)
    sorted_latencies = sorted(latencies)
    print({
        "requests": REQUESTS,
        "concurrency": CONCURRENCY,
        "avg_ms": round(statistics.mean(latencies) * 1000, 2),
        "p95_ms": round(sorted_latencies[p95_index] * 1000, 2),
    })


if __name__ == "__main__":
    asyncio.run(main())
