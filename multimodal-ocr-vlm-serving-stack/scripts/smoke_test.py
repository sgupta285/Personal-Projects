import asyncio
from pathlib import Path

import httpx

BASE = 'http://127.0.0.1:8000'


async def main() -> None:
    async with httpx.AsyncClient(timeout=10.0) as client:
        health = await client.get(f'{BASE}/healthz')
        health.raise_for_status()
        payload = {
            'items': [
                {'document_id': 'smoke-doc-1', 'text_hint': 'Invoice number 77', 'image_width': 1280, 'image_height': 720, 'page_count': 1}
            ],
            'prompt': 'Summarize this image'
        }
        submit = await client.post(f'{BASE}/pipeline', json=payload)
        submit.raise_for_status()
        job_id = submit.json()['job_id']
        for _ in range(40):
            resp = await client.get(f'{BASE}/jobs/{job_id}')
            resp.raise_for_status()
            data = resp.json()
            if data['status'] == 'completed':
                print('Smoke test completed:', data['result']['engine'])
                return
            await asyncio.sleep(0.1)
        raise RuntimeError('Timed out waiting for pipeline job completion')


if __name__ == '__main__':
    asyncio.run(main())
