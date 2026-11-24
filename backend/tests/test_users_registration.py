"""Tests de POST /api/users: alta de empleado (PEB-43 / HU-07)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import or_, select

from app.core.database import SessionLocal
from app.core.security import verify_password
from app.models.department import Department
from app.models.user import User

DEPARTMENT_NAME = "Test PEB15 Dept"
EMPLOYEE_EMAIL = "alta.test@pluxee.test"
SECOND_EMAIL = "alta.second@pluxee.test"
LOGIN_EMAIL = "alta.login@pluxee.test"
ADMIN_EMAIL = "alta.admin@pluxee.test"

TEST_EMAILS = (
    EMPLOYEE_EMAIL,
    EMPLOYEE_EMAIL.upper(),
    SECOND_EMAIL,
    LOGIN_EMAIL,
    ADMIN_EMAIL,
)


def _purge() -> None:
    with SessionLocal() as db:
        department = db.scalar(
            select(Department).where(Department.name == DEPARTMENT_NAME)
        )
        statement = select(User).where(User.email.in_(TEST_EMAILS))
        if department is not None:
            statement = select(User).where(
                or_(
                    User.email.in_(TEST_EMAILS),
                    User.department_id == department.id,
                )
            )
        for user in db.scalars(statement).all():
            db.delete(user)
        db.commit()

        if department is not None:
            db.delete(department)
            db.commit()


@pytest.fixture(autouse=True)
def department():
    """Crea un departamento directamente en la BD para los tests."""
    _purge()
    with SessionLocal() as db:
        dept = Department(name=DEPARTMENT_NAME, currency="EUR", is_active=True)
        db.add(dept)
        db.commit()
        db.refresh(dept)
        dept_id = dept.id
    yield {"id": dept_id, "name": DEPARTMENT_NAME, "currency": "EUR"}
    _purge()


@pytest.fixture()
def admin_headers(auth_headers, user_factory) -> dict[str, str]:
    admin = user_factory(
        ADMIN_EMAIL, full_name="Test Admin", role="ADMIN", department_id=None
    )
    return auth_headers(admin)


def _payload(department_id: int, **overrides) -> dict:
    payload = {
        "full_name": "Empleado de Alta",
        "email": EMPLOYEE_EMAIL,
        "temporary_password": "Temporal1234!",
        "department_id": department_id,
    }
    payload.update(overrides)
    return payload


def _stored_user(email: str) -> User | None:
    with SessionLocal() as db:
        return db.scalar(select(User).where(User.email == email))


def test_register_employee_creates_account_with_security_defaults(
    client: TestClient, department, admin_headers
) -> None:
    response = client.post(
        "/api/users",
        headers=admin_headers,
        json=_payload(department["id"], email=f"  {EMPLOYEE_EMAIL.upper()}  "),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == EMPLOYEE_EMAIL
    assert body["full_name"] == "Empleado de Alta"
    assert body["role"] == "EMPLOYEE"
    assert body["department_id"] == department["id"]
    assert body["is_active"] is True
    assert body["must_change_password"] is True
    assert "password_hash" not in body
    assert "temporary_password" not in body

    stored = _stored_user(EMPLOYEE_EMAIL)
    assert stored is not None
    assert stored.password_hash != "Temporal1234!"
    assert verify_password("Temporal1234!", stored.password_hash) is True
    assert verify_password("OtraClave1234!", stored.password_hash) is False
    assert stored.must_change_password is True
    assert stored.role == "EMPLOYEE"


def test_register_duplicate_email_returns_409(
    client: TestClient, department, admin_headers
) -> None:
    first = client.post(
        "/api/users", headers=admin_headers, json=_payload(department["id"])
    )
    assert first.status_code == 201

    second = client.post(
        "/api/users",
        headers=admin_headers,
        json=_payload(department["id"], email=EMPLOYEE_EMAIL.upper()),
    )

    assert second.status_code == 409
    assert second.json()["error"]["code"] == "conflict"
    assert _stored_user(EMPLOYEE_EMAIL) is not None


def test_register_unknown_department_returns_404(
    client: TestClient, department, admin_headers
) -> None:
    response = client.post(
        "/api/users", headers=admin_headers, json=_payload(99999)
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert _stored_user(EMPLOYEE_EMAIL) is None


def test_register_requires_department(
    client: TestClient, department, admin_headers
) -> None:
    payload = _payload(department["id"])
    del payload["department_id"]

    response = client.post("/api/users", headers=admin_headers, json=payload)

    assert response.status_code == 422


def test_register_rejects_short_temporary_password(
    client: TestClient, department, admin_headers
) -> None:
    response = client.post(
        "/api/users",
        headers=admin_headers,
        json=_payload(department["id"], temporary_password="corta"),
    )

    assert response.status_code == 422
    assert _stored_user(EMPLOYEE_EMAIL) is None


def test_register_rejects_invalid_email(
    client: TestClient, department, admin_headers
) -> None:
    response = client.post(
        "/api/users",
        headers=admin_headers,
        json=_payload(department["id"], email="no-es-un-correo"),
    )

    assert response.status_code == 422


def test_register_without_token_returns_401(
    client: TestClient, department
) -> None:
    response = client.post("/api/users", json=_payload(department["id"]))

    assert response.status_code == 401
    assert _stored_user(EMPLOYEE_EMAIL) is None


def test_register_as_employee_returns_403(
    client: TestClient, department, auth_headers, user_factory
) -> None:
    employee = user_factory(LOGIN_EMAIL)

    response = client.post(
        "/api/users",
        headers=auth_headers(employee),
        json=_payload(department["id"]),
    )

    assert response.status_code == 403
    assert _stored_user(EMPLOYEE_EMAIL) is None


def test_registered_employee_must_change_password_on_login(
    client: TestClient, department, admin_headers
) -> None:
    created = client.post(
        "/api/users", headers=admin_headers, json=_payload(department["id"])
    )
    assert created.status_code == 201

    login = client.post(
        "/api/login",
        json={"email": EMPLOYEE_EMAIL, "password": "Temporal1234!"},
    )

    assert login.status_code == 200
    body = login.json()
    assert body["user"]["must_change_password"] is True
    assert body["access_token"]
