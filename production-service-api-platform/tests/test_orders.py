def test_list_orders_v1(client, api_key_headers):
    response = client.get('/api/v1/orders', headers=api_key_headers)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload['data']) == 3
    assert payload['meta']['total'] == 3


def test_create_order_v2_idempotent(client, api_key_headers):
    body = {
        'customer_name': 'Acme',
        'item_sku': 'SKU-100',
        'quantity': 2,
        'total_cents': 5000,
        'notes': 'first submit',
    }
    headers = dict(api_key_headers)
    headers['Idempotency-Key'] = 'idem-1'
    first = client.post('/api/v2/orders', json=body, headers=headers)
    second = client.post('/api/v2/orders', json=body, headers=headers)
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()['id'] == second.json()['id']


def test_bearer_token_access(client, bearer_headers):
    response = client.get('/api/v1/orders', headers=bearer_headers)
    assert response.status_code == 200


def test_validation_error(client, api_key_headers):
    response = client.post('/api/v1/orders', json={'customer_name': 'x', 'item_sku': '12', 'quantity': 0, 'total_cents': 0}, headers=api_key_headers)
    assert response.status_code == 422


def test_unauthenticated_request(client):
    response = client.get('/api/v1/orders')
    assert response.status_code == 401


def test_update_not_found(client, api_key_headers):
    response = client.patch('/api/v1/orders/999', json={'status': 'fulfilled', 'notes': 'done'}, headers=api_key_headers)
    assert response.status_code == 404
