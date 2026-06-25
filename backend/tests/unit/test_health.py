"""Smoke tests for the health endpoints — verify the app starts and responds."""


def test_liveness_returns_ok(client):
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data


def test_readiness_returns_ok(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
