from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["graphql"] == "/graphql"
    assert data["health"] == "/health"
