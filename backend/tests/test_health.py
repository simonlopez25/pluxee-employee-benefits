from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_200() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200


def test_health_body_shape() -> None:
    response = client.get("/api/health")
    body = response.json()

    assert body["status"] == "ok"
    assert body["database"] in {"up", "down"}


def test_unknown_route_returns_404() -> None:
    response = client.get("/api/nope")

    assert response.status_code == 404
