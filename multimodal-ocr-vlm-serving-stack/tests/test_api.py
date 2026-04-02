import asyncio
from pathlib import Path
import shutil

from httpx import ASGITransport, AsyncClient

from app.api.deps import orchestrator, store
from app.api.main import app


def reset_job_store() -> None:
    shutil.rmtree(Path(store.root), ignore_errors=True)
    Path(store.root).mkdir(parents=True, exist_ok=True)


async def wait_for_completion(client: AsyncClient, job_id: str) -> dict:
    for _ in range(50):
        response = await client.get(f'/jobs/{job_id}')
        response.raise_for_status()
        data = response.json()
        if data['status'] == 'completed':
            return data
        await asyncio.sleep(0.05)
    raise AssertionError('job did not complete')


async def _run_pipeline_test() -> None:
    reset_job_store()
    await orchestrator.start()
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://testserver') as client:
            payload = {
                'items': [{'document_id': 'doc-1', 'text_hint': 'Quarterly results', 'image_width': 1400, 'image_height': 900, 'page_count': 2}],
                'prompt': 'Summarize this image'
            }
            response = await client.post('/pipeline', json=payload)
            assert response.status_code == 200
            job_id = response.json()['job_id']
            data = await wait_for_completion(client, job_id)
            assert data['result']['engine'] == 'mock-pipeline'
            assert data['result']['documents'][0]['entities'][0]['type'] == 'document_id'
    finally:
        await orchestrator.stop()


def test_pipeline_job() -> None:
    asyncio.run(_run_pipeline_test())
