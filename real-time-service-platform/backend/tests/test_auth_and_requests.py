from app.services.circuit_breaker import service_circuit_breaker


def register_and_login(client, username='alice', password='secret123', role='operator'):
    client.post('/v1/auth/register', json={
        'username': username,
        'full_name': username.title(),
        'password': password,
        'role': role,
    })
    response = client.post('/v1/auth/login', data={'username': username, 'password': password})
    token = response.json()['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_sync_request_flow(client):
    headers = register_and_login(client)
    response = client.post('/v1/requests/sync', headers=headers, json={
        'kind': 'checkout',
        'payload': {'amount': 12.3},
        'priority': 2,
    })
    assert response.status_code == 200
    body = response.json()
    assert body['status'] == 'completed'
    assert body['downstream_latency_ms'] > 0


def test_async_request_flow(client):
    headers = register_and_login(client, username='bob')
    response = client.post('/v1/requests/async', headers=headers, json={
        'kind': 'shipment_update',
        'payload': {'tracking_number': 'TRK123'},
        'priority': 4,
    })
    assert response.status_code == 200
    assert response.json()['status'] == 'queued'


def test_circuit_breaker_opens_after_repeated_failures(client):
    headers = register_and_login(client, username='carl')
    for _ in range(3):
        response = client.post('/v1/requests/sync', headers=headers, json={
            'kind': 'fragile_dependency',
            'payload': {'simulate_failure': True},
            'priority': 1,
        })
        assert response.status_code == 502
    assert service_circuit_breaker.state.value == 'open'


def test_rate_limiting_exists(client):
    headers = register_and_login(client, username='rate')
    too_many = None
    for _ in range(80):
        response = client.get('/v1/system/trace', headers=headers)
        if response.status_code == 429:
            too_many = response
            break
    assert too_many is not None
