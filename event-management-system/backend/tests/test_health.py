import pytest
from django.test import Client

@pytest.mark.django_db
def test_healthcheck():
    client = Client()
    response = client.get('/health/')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
