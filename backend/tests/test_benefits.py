from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select

from app.core.database import SessionLocal
from app.main import app
from app.models.benefit import Benefit

client = TestClient(app)

TEST_NAME_PREFIX = "Test CRUD"


def _delete_test_benefits() -> None:
    with SessionLocal() as db:
        statement = delete(Benefit).where(
            func.lower(Benefit.name).startswith(TEST_NAME_PREFIX.lower())
        )
        db.execute(statement)
        db.commit()


@pytest.fixture(autouse=True)
def clean_test_benefits():
    _delete_test_benefits()
    yield
    _delete_test_benefits()


def _create_benefit(**overrides) -> dict:
    payload = {"name": f"{TEST_NAME_PREFIX} Base", **overrides}
    response = client.post("/api/benefits", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _nonexistent_benefit_id() -> int:
    with SessionLocal() as db:
        max_id = db.scalar(select(func.max(Benefit.id)))
    return (max_id or 0) + 1000


def test_create_benefit_returns_201() -> None:
    response = client.post(
        "/api/benefits",
        json={
            "name": f"{TEST_NAME_PREFIX} Creación",
            "description": "Beneficio de prueba",
            "is_basic": True,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert isinstance(body["id"], int)
    assert body["name"] == f"{TEST_NAME_PREFIX} Creación"
    assert body["description"] == "Beneficio de prueba"
    assert body["is_basic"] is True
    assert body["is_active"] is True


def test_create_benefit_without_description_stores_empty_string() -> None:
    response = client.post(
        "/api/benefits",
        json={"name": f"{TEST_NAME_PREFIX} Sin descripción"},
    )

    assert response.status_code == 201
    assert response.json()["description"] == ""


def test_create_duplicate_name_returns_409_including_case_variants() -> None:
    _create_benefit(name=f"{TEST_NAME_PREFIX} Duplicado")

    exact = client.post(
        "/api/benefits",
        json={"name": f"{TEST_NAME_PREFIX} Duplicado"},
    )
    different_case = client.post(
        "/api/benefits",
        json={"name": f"{TEST_NAME_PREFIX.lower()} DUPLICADO"},
    )

    for response in (exact, different_case):
        assert response.status_code == 409
        assert response.json()["error"]["message"] == "Ya existe un beneficio con ese nombre"


def test_create_blank_name_returns_422() -> None:
    response = client.post("/api/benefits", json={"name": "   "})

    assert response.status_code == 422
    assert "El nombre no puede estar vacío" in response.text


def test_list_benefits_and_filters() -> None:
    _create_benefit(name=f"{TEST_NAME_PREFIX} List Activo", is_basic=True)
    _create_benefit(name=f"{TEST_NAME_PREFIX} List Inactivo", is_active=False)

    all_response = client.get("/api/benefits")
    assert all_response.status_code == 200
    all_benefits = all_response.json()
    all_names = {benefit["name"] for benefit in all_benefits}
    assert {f"{TEST_NAME_PREFIX} List Activo", f"{TEST_NAME_PREFIX} List Inactivo"} <= all_names
    ids = [benefit["id"] for benefit in all_benefits]
    assert ids == sorted(ids)

    active_response = client.get("/api/benefits", params={"is_active": True})
    assert active_response.status_code == 200
    active_benefits = active_response.json()
    active_names = {benefit["name"] for benefit in active_benefits}
    assert all(benefit["is_active"] for benefit in active_benefits)
    assert f"{TEST_NAME_PREFIX} List Activo" in active_names
    assert f"{TEST_NAME_PREFIX} List Inactivo" not in active_names

    basic_response = client.get("/api/benefits", params={"is_basic": True})
    assert basic_response.status_code == 200
    basic_benefits = basic_response.json()
    assert all(benefit["is_basic"] for benefit in basic_benefits)
    assert f"{TEST_NAME_PREFIX} List Activo" in {b["name"] for b in basic_benefits}

    by_name = client.get("/api/benefits", params={"order_by": "name"})
    assert by_name.status_code == 200
    test_names = [
        benefit["name"]
        for benefit in by_name.json()
        if benefit["name"].startswith(TEST_NAME_PREFIX)
    ]
    assert test_names == sorted(test_names)


def test_update_benefit_with_put_and_rejects_duplicate_name() -> None:
    _create_benefit(name=f"{TEST_NAME_PREFIX} PUT A")
    second = _create_benefit(name=f"{TEST_NAME_PREFIX} PUT B")

    duplicated = client.put(
        f"/api/benefits/{second['id']}",
        json={"name": f"{TEST_NAME_PREFIX.lower()} PUT A"},
    )
    assert duplicated.status_code == 409
    assert duplicated.json()["error"]["message"] == "Ya existe un beneficio con ese nombre"

    response = client.put(
        f"/api/benefits/{second['id']}",
        json={
            "name": f"{TEST_NAME_PREFIX} PUT B",
            "description": "Descripción actualizada",
            "is_basic": True,
            "is_active": False,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["description"] == "Descripción actualizada"
    assert body["is_basic"] is True
    assert body["is_active"] is False

    partial = client.put(
        f"/api/benefits/{second['id']}",
        json={"name": f"{TEST_NAME_PREFIX} PUT B2"},
    )
    assert partial.status_code == 200
    assert partial.json()["description"] == "Descripción actualizada"
    assert partial.json()["name"] == f"{TEST_NAME_PREFIX} PUT B2"


def test_patch_deactivates_benefit_and_keeps_it_in_database() -> None:
    created = _create_benefit(name=f"{TEST_NAME_PREFIX} Baja lógica")

    response = client.patch(
        f"/api/benefits/{created['id']}",
        json={"is_active": False},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["is_active"] is False
    assert body["name"] == f"{TEST_NAME_PREFIX} Baja lógica"

    with SessionLocal() as db:
        stored = db.get(Benefit, created["id"])
    assert stored is not None
    assert stored.is_active is False

    detail = client.get(f"/api/benefits/{created['id']}")
    assert detail.status_code == 200
    assert detail.json()["is_active"] is False


def test_patch_without_fields_returns_422() -> None:
    created = _create_benefit(name=f"{TEST_NAME_PREFIX} PATCH vacío")

    response = client.patch(f"/api/benefits/{created['id']}", json={})

    assert response.status_code == 422
    assert "Se debe proporcionar al menos un campo" in response.text


def test_missing_benefit_returns_404() -> None:
    benefit_id = _nonexistent_benefit_id()

    detail = client.get(f"/api/benefits/{benefit_id}")
    updated = client.put(
        f"/api/benefits/{benefit_id}",
        json={"name": f"{TEST_NAME_PREFIX} No existe"},
    )
    patched = client.patch(f"/api/benefits/{benefit_id}", json={"is_active": False})

    for response in (detail, updated, patched):
        assert response.status_code == 404
        assert response.json()["error"]["message"] == "Beneficio no encontrado"
