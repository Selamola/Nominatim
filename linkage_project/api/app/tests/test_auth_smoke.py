import random
from fastapi.testclient import TestClient
from app.main import app


def test_auth_flow():
    client = TestClient(app)
    email = f"user{random.randint(0,99999)}@example.com"
    password = "Secret123"
    r = client.post('/auth/register', json={'email': email, 'password': password, 'name': 'Tester'})
    assert r.status_code == 200
    r = client.post('/auth/login', data={'username': email, 'password': password})
    assert r.status_code == 200
    token = r.json()['access_token']
    r = client.get('/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 200
    assert r.json()['email'] == email
