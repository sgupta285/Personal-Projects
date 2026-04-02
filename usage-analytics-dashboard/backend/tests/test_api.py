from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthcheck():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_metric_catalog_contains_workspaces():
    response = client.get('/metric-catalog')
    assert response.status_code == 200
    payload = response.json()
    assert 'acme-cloud' in payload['workspaces']
    assert 'feature' in payload['dimensions']


def test_summary_has_totals_and_time_series():
    response = client.get('/usage/summary', params={'workspace_id': 'acme-cloud', 'interval': 'day'})
    assert response.status_code == 200
    payload = response.json()
    assert payload['totals']['request_units'] > 0
    assert len(payload['time_series']) > 0


def test_breakdown_respects_dimension():
    response = client.get('/usage/breakdown', params={'workspace_id': 'acme-cloud', 'dimension': 'endpoint'})
    assert response.status_code == 200
    payload = response.json()
    assert payload['dimension'] == 'endpoint'
    assert len(payload['rows']) > 0


def test_csv_export_returns_attachment():
    response = client.get('/usage/export.csv')
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('text/csv')
    assert 'attachment;' in response.headers['content-disposition']
