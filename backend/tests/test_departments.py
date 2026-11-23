"""Tests del listado de departamentos (soporte de la UI de presupuestos)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_departments_returns_expected_shape() -> None:
    response = client.get("/api/departments")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) > 0  # el seed crea 3 departamentos
    for department in body:
        assert set(department) == {"id", "name", "is_active"}
        assert isinstance(department["id"], int)
        assert isinstance(department["name"], str)
        assert isinstance(department["is_active"], bool)


def test_list_departments_is_sorted_by_name() -> None:
    response = client.get("/api/departments")

    names = [department["name"] for department in response.json()]
    assert names == sorted(names)


def test_list_departments_filters_by_is_active() -> None:
    all_departments = client.get("/api/departments").json()
    active = client.get("/api/departments", params={"is_active": True}).json()
    inactive = client.get("/api/departments", params={"is_active": False}).json()

    assert all(department["is_active"] for department in active)
    assert not any(department["is_active"] for department in inactive)
    # El filtro activo es un subconjunto del listado completo
    assert {d["id"] for d in active} <= {d["id"] for d in all_departments}
