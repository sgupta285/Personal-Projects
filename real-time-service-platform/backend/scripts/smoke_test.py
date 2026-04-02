from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from app.db.database import Base, engine
from app.main import app

Base.metadata.create_all(bind=engine)

with TestClient(app) as client:

    register = client.post('/v1/auth/register', json={
        'username': 'smoke',
        'full_name': 'Smoke Test',
        'password': 'secret123',
        'role': 'operator'
    })
    if register.status_code not in {200, 409}:
        raise SystemExit(f'register failed: {register.text}')

    auth = client.post('/v1/auth/login', data={'username': 'smoke', 'password': 'secret123'})
    if auth.status_code != 200:
        raise SystemExit(f'login failed: {auth.text}')

    token = auth.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    resp = client.post('/v1/requests/sync', json={
        'kind': 'payment_authorization',
        'payload': {'order_id': 'ord_1001', 'amount': 42.5},
        'priority': 2,
    }, headers=headers)
    if resp.status_code != 200:
        raise SystemExit(f'sync request failed: {resp.text}')
    print('Smoke test passed.')
