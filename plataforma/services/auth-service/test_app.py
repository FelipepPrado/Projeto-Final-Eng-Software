import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Testa se o endpoint /health retorna status 200"""
    rv = client.get('/health')
    assert rv.status_code == 200
    assert b'funcionando' in rv.data