from pathlib import Path
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from app.db.database import Base, engine
from app.main import app

Base.metadata.create_all(bind=engine)

with TestClient(app) as client:

    client.post('/v1/auth/register', json={
        'username': 'bench',
        'full_name': 'Bench User',
        'password': 'secret123',
        'role': 'operator'
    })
    auth = client.post('/v1/auth/login', data={'username': 'bench', 'password': 'secret123'})
    token = auth.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    latencies = []
    for index in range(25):
        started = time.perf_counter()
        response = client.post('/v1/requests/sync', json={
            'kind': 'benchmark_event',
            'payload': {'seq': index},
            'priority': 3,
        }, headers=headers)
        response.raise_for_status()
        latencies.append((time.perf_counter() - started) * 1000)

    print({
        'requests': len(latencies),
        'avg_ms': round(statistics.mean(latencies), 2),
        'p95_ms': round(sorted(latencies)[int(len(latencies) * 0.95) - 1], 2),
        'max_ms': round(max(latencies), 2),
    })
