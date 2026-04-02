import os
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

fd, path = tempfile.mkstemp(suffix='.db')
os.close(fd)
os.environ['DATABASE_URL'] = f'sqlite:///{path}'
os.environ['ENABLE_REDIS'] = 'false'
os.environ['JWT_SECRET'] = 'test-secret'

from app.db import init_db, SessionLocal
from app.main import create_app
from app.models import ApiClient, Order
from app.services.tokens import create_access_token, hash_api_key
from app.core.config import get_settings


@pytest.fixture()
def client():
    app = create_app()
    init_db()
    session = SessionLocal()
    session.query(Order).delete()
    session.query(ApiClient).delete()
    session.add(ApiClient(
        name='test-partner',
        client_id='test-partner',
        api_key_hash=hash_api_key('test-api-key'),
        auth_mode='api_key',
        rate_limit_per_minute=100,
        daily_quota=1000,
        scopes='orders:read orders:write',
        is_active=True,
    ))
    for idx in range(1, 4):
        session.add(Order(
            external_id=f'order-{idx}',
            customer_name=f'Customer {idx}',
            item_sku=f'SKU-{idx}',
            quantity=idx,
            status='pending',
            total_cents=idx * 100,
            notes='fixture',
        ))
    session.commit()
    session.close()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def api_key_headers():
    return {'X-API-Key': 'test-api-key'}


@pytest.fixture()
def bearer_headers():
    token = create_access_token('internal-admin', ['orders:read', 'orders:write'], 'service', get_settings())
    return {'Authorization': f'Bearer {token}'}
