"""Tests de departamentos (/api/departments)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select

from app.core.database import SessionLocal
from app.main import app
from app.models.department import Department

client = TestClient(app)

TEST_NAME_PREFIX = "Test PEB14 Dept"

EXPECTED_LIST_KEYS = {
    "id",
    "name",
    "currency",
    "is_active",
    "created_at",
    "employee_count",
    "packages",
}


def _delete_test_departments() -> None:
    """Borra únicamente los departamentos de prueba creados por este módulo."""
    with SessionLocal() as db:
        db.execute(
            delete(Department).where(
                func.lower(Department.name).startswith(TEST_NAME_PREFIX.lower())
            )
        )
        db.commit()


@pytest.fixture(autouse=True)
def clean_test_departments():
    """Limpia los departamentos de prueba antes y después de cada test."""
    _delete_test_departments()
    yield
    _delete_test_departments()


def _create_department(**overrides) -> dict:
    payload = {"name": f"{TEST_NAME_PREFIX} Base", "currency": "EUR", **overrides}
    response = client.post("/api/departments", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _nonexistent_department_id() -> int:
    with SessionLocal() as db:
        max_id = db.scalar(select(func.max(Department.id)))
    return (max_id or 0) + 1000


def test_list_departments_returns_expected_shape() -> None:
    response = client.get("/api/departments")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) > 0
    for department in body:
        assert set(department) == EXPECTED_LIST_KEYS
        assert isinstance(department["id"], int)
        assert isinstance(department["name"], str)
        assert isinstance(department["is_active"], bool)
        assert isinstance(department["employee_count"], int)
        assert isinstance(department["packages"], list)
        for pkg in department["packages"]:
            assert set(pkg) == {"id", "name"}
            assert isinstance(pkg["id"], int)
            assert isinstance(pkg["name"], str)


def test_list_departments_seed_counts_and_packages() -> None:
    response = client.get("/api/departments")
    assert response.status_code == 200
    by_name = {dept["name"]: dept for dept in response.json()}

    assert by_name["Ventas"]["employee_count"] == 2
    assert {p["name"] for p in by_name["Ventas"]["packages"]} == {
        "Comida",
        "Comida y transporte",
    }

    assert by_name["Ingeniería"]["employee_count"] == 2
    assert {p["name"] for p in by_name["Ingeniería"]["packages"]} == {
        "Formación",
        "Transporte",
    }

    assert by_name["Marketing"]["employee_count"] == 1
    assert {p["name"] for p in by_name["Marketing"]["packages"]} == {
        "Comida y transporte flexible",
        "Guardería",
    }


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
    assert {d["id"] for d in active} <= {d["id"] for d in all_departments}


def test_create_department_returns_201_and_normalizes_currency() -> None:
    response = client.post(
        "/api/departments",
        json={"name": f"{TEST_NAME_PREFIX} Producto", "currency": "usd"},
    )

    assert response.status_code == 201
    body = response.json()
    assert isinstance(body["id"], int)
    assert body["name"] == f"{TEST_NAME_PREFIX} Producto"
    assert body["currency"] == "USD"
    assert body["is_active"] is True


def test_create_duplicate_department_name_returns_409() -> None:
    _create_department(name=f"{TEST_NAME_PREFIX} Duplicado")

    exact = client.post(
        "/api/departments",
        json={"name": f"{TEST_NAME_PREFIX} Duplicado", "currency": "EUR"},
    )
    different_case = client.post(
        "/api/departments",
        json={"name": f"{TEST_NAME_PREFIX.lower()} duplicado", "currency": "EUR"},
    )

    for response in (exact, different_case):
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "conflict"


def test_update_department_with_put_and_rejects_duplicate_name() -> None:
    _create_department(name=f"{TEST_NAME_PREFIX} Primero")
    second = _create_department(name=f"{TEST_NAME_PREFIX} Segundo")

    conflict = client.put(
        f"/api/departments/{second['id']}",
        json={"name": f"{TEST_NAME_PREFIX} primero", "currency": "EUR"},
    )
    assert conflict.status_code == 409

    updated = client.put(
        f"/api/departments/{second['id']}",
        json={"name": f"{TEST_NAME_PREFIX} Segundo Editado", "currency": "gbp"},
    )
    assert updated.status_code == 200
    body = updated.json()
    assert body["name"] == f"{TEST_NAME_PREFIX} Segundo Editado"
    assert body["currency"] == "GBP"


def test_get_and_update_missing_department_returns_404() -> None:
    missing_id = _nonexistent_department_id()

    get_resp = client.get(f"/api/departments/{missing_id}")
    put_resp = client.put(
        f"/api/departments/{missing_id}",
        json={"name": f"{TEST_NAME_PREFIX} Inexistente", "currency": "EUR"},
    )

    for resp in (get_resp, put_resp):
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "not_found"