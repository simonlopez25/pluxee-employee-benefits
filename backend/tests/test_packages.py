from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select

from app.core.database import SessionLocal
from app.main import app
from app.models.benefit import Benefit
from app.models.department import Department
from app.models.package import Package
from app.models.package_benefit import PackageBenefit

client = TestClient(app)

TEST_NAME_PREFIX = "Test PKG"


def _delete_test_packages() -> None:
    with SessionLocal() as db:
        test_ids = select(Package.id).where(
            func.lower(Package.name).startswith(TEST_NAME_PREFIX.lower())
        )
        db.execute(delete(PackageBenefit).where(PackageBenefit.package_id.in_(test_ids)))
        db.execute(delete(Package).where(Package.id.in_(test_ids)))
        db.commit()


@pytest.fixture(autouse=True)
def clean_test_packages():
    _delete_test_packages()
    yield
    _delete_test_packages()

def _active_department_id() -> int:
        with SessionLocal() as db:
            statement = (
                select(Department.id)
                .where(Department.is_active.is_(True))
                .order_by(Department.id)
            )
            return db.scalar(statement)

def _active_benefit_ids(count: int) -> list[int]:
        with SessionLocal() as db:
            statement = (
                select(Benefit.id)
                .where(Benefit.is_active.is_(True))
                .order_by(Benefit.id)
                .limit(count)
            )
            return list(db.scalars(statement).all())


def test_create_mono_package_returns_201() -> None:
        department_id = _active_department_id()
        benefit_ids = _active_benefit_ids(1)

        response = client.post(
            "/api/packages",
            json={
                "name": f"{TEST_NAME_PREFIX} Mono",
                "default_amount": "60.00",
                "department_id": department_id,
                "benefit_ids": benefit_ids,
            },
        )

        assert response.status_code == 201, response.text
        body = response.json()
        assert body["name"] == f"{TEST_NAME_PREFIX} Mono"
        assert body["department_id"] == department_id
        assert body["default_amount"] == "60.00"
        assert [benefit["id"] for benefit in body["benefits"]] == benefit_ids
        assert body["package_type"] == "MONO"
        assert body["is_active"] is True

def _create_package(**overrides) -> dict:
    payload = {
        "name": f"{TEST_NAME_PREFIX} Base",
        "default_amount": "50.00",
        "department_id": _active_department_id(),
        "benefit_ids": _active_benefit_ids(1),
        **overrides,
    }
    response = client.post("/api/packages", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_create_multi_package_returns_multi_type() -> None:
    benefit_ids = _active_benefit_ids(2)

    body = _create_package(name=f"{TEST_NAME_PREFIX} Multi", benefit_ids=benefit_ids)

    assert [benefit["id"] for benefit in body["benefits"]] == benefit_ids
    assert body["package_type"] == "MULTI"


def test_duplicate_name_in_same_department_returns_409() -> None:
    _create_package(name=f"{TEST_NAME_PREFIX} Repetido")

    response = client.post(
        "/api/packages",
        json={
            "name": f"{TEST_NAME_PREFIX} REPETIDO",
            "default_amount": "50.00",
            "department_id": _active_department_id(),
            "benefit_ids": _active_benefit_ids(1),
        },
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"
def _nonexistent_id(model) -> int:
    with SessionLocal() as db:
        max_id = db.scalar(select(func.max(model.id)))
    return (max_id or 0) + 1000


def test_create_with_nonexistent_department_returns_404() -> None:
    response = client.post(
        "/api/packages",
        json={
            "name": f"{TEST_NAME_PREFIX} Sin departamento",
            "default_amount": "50.00",
            "department_id": _nonexistent_id(Department),
            "benefit_ids": _active_benefit_ids(1),
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_create_with_nonexistent_benefit_returns_404() -> None:
    response = client.post(
        "/api/packages",
        json={
            "name": f"{TEST_NAME_PREFIX} Sin beneficio",
            "default_amount": "50.00",
            "department_id": _active_department_id(),
            "benefit_ids": [_nonexistent_id(Benefit)],
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


@pytest.mark.parametrize(
    "overrides",
    [
        {"name": "   "},
        {"default_amount": "-10.00"},
        {"benefit_ids": []},
        {"benefit_ids": [1, 1]},
    ],
)
def test_invalid_payload_returns_422(overrides: dict) -> None:
    payload = {
        "name": f"{TEST_NAME_PREFIX} Inválido",
        "default_amount": "50.00",
        "department_id": _active_department_id(),
        "benefit_ids": _active_benefit_ids(1),
        **overrides,
    }

    response = client.post("/api/packages", json=payload)

    assert response.status_code == 422

def test_get_package_returns_created_package() -> None:
    created = _create_package(name=f"{TEST_NAME_PREFIX} Consulta")

    response = client.get(f"/api/packages/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_nonexistent_package_returns_404() -> None:
    response = client.get(f"/api/packages/{_nonexistent_id(Package)}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_list_filters_by_department() -> None:
    department_id = _active_department_id()
    created = _create_package(name=f"{TEST_NAME_PREFIX} Filtro", department_id=department_id)

    response = client.get("/api/packages", params={"department_id": department_id})

    assert response.status_code == 200
    packages = response.json()
    assert all(package["department_id"] == department_id for package in packages)
    assert created["id"] in [package["id"] for package in packages]

def test_database_rejects_same_name_with_different_case() -> None:
        department_id = _active_department_id()
        response = client.post(
            "/api/packages",
            json={
                "name": f"{TEST_NAME_PREFIX} Mayusculas",
                "default_amount": "10.00",
                "department_id": department_id,
                "benefit_ids": _active_benefit_ids(1),
            },
        )
        assert response.status_code == 201, response.text

        with SessionLocal() as db:
            db.add(
                Package(
                    name=f"{TEST_NAME_PREFIX} Mayusculas".upper(),
                    default_amount=10,
                    department_id=department_id,
                )
            )
            with pytest.raises(IntegrityError):
                db.commit()