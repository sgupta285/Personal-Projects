import asyncio
import statistics
import time

import httpx

BASE = 'http://127.0.0.1:8000'


async def submit(client: httpx.AsyncClient, idx: int) -> str:
    payload = {
        'items': [
            {
                'document_id': f'bench-{idx}',
                'text_hint': f'Bench text {idx}',
                'image_width': 1920,
                'image_height': 1080,
                'page_count': 2,
            }
        ],
        'prompt': 'Extract layout and summarize'
    }
    resp = await client.post(f'{BASE}/pipeline', json=payload)
    resp.raise_for_status()
    return resp.json()['job_id']


async def wait_for_job(client: httpx.AsyncClient, job_id: str) -> float:
    start = time.perf_counter()
    for _ in range(100):
        resp = await client.get(f'{BASE}/jobs/{job_id}')
        resp.raise_for_status()
        status = resp.json()['status']
        if status == 'completed':
            return time.perf_counter() - start
        await asyncio.sleep(0.05)
    raise RuntimeError(f'job {job_id} did not finish in time')


async def main() -> None:
    async with httpx.AsyncClient(timeout=20.0) as client:
        job_ids = await asyncio.gather(*(submit(client, idx) for idx in range(20)))
        latencies = await asyncio.gather(*(wait_for_job(client, job_id) for job_id in job_ids))
    print({
        'jobs': len(latencies),
        'avg_seconds': round(statistics.mean(latencies), 4),
        'p95_seconds': round(sorted(latencies)[int(len(latencies) * 0.95) - 1], 4),
        'max_seconds': round(max(latencies), 4),
    })


if __name__ == '__main__':
    asyncio.run(main())
