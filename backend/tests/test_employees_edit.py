"""Tests de PATCH /api/users/{user_id}: edición de empleados (PEB-16 / HU-08)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.models.user import User

ADMIN_EMAIL = "test-admin-peb16@pluxee.test"
SECOND_ADMIN_EMAIL = "test-admin2-peb16@pluxee.test"
EMPLOYEE_EMAIL = "test-employee-peb16@pluxee.test"
SECOND_EMPLOYEE_EMAIL = "test-employee2-peb16@pluxee.test"
DUPLICATE_EMAIL = "test-duplicate-peb16@pluxee.test"
EDITED_EMAIL = "edited.employee-peb16@pluxee.test"

TEST_USER_EMAILS = (
    ADMIN_EMAIL,
    SECOND_ADMIN_EMAIL,
    EMPLOYEE_EMAIL,
    SECOND_EMPLOYEE_EMAIL,
    DUPLICATE_EMAIL,
    EDITED_EMAIL,
    EDITED_EMAIL.upper(),
)


@pytest.fixture(autouse=True)
def cleanup(delete_users):
    delete_users(*TEST_USER_EMAILS)
    yield
    delete_users(*TEST_USER_EMAILS)


@pytest.fixture()
def admin(user_factory):
    return user_factory(ADMIN_EMAIL, full_name="Test Admin", role="ADMIN", department_id=None)


@pytest.fixture()
def employee(user_factory):
    return user_factory(EMPLOYEE_EMAIL, full_name="Test Employee")


def _get_user(user_id: int) -> User:
    with SessionLocal() as db:
        return db.get(User, user_id)


def test_edit_employee_success_updates_fields(
    client: TestClient, auth_headers, admin, employee
) -> None:
    response = client.patch(
        f"/api/users/{employee.id}",
        headers=auth_headers(admin),
        json={
            "full_name": "Nombre Actualizado",
            "email": EDITED_EMAIL,
            "department_id": 2,
            "role": "EMPLOYEE",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == employee.id
    assert body["full_name"] == "Nombre Actualizado"
    assert body["email"] == EDITED_EMAIL
    assert body["department_id"] == 2
    assert body["role"] == "EMPLOYEE"

    stored = _get_user(employee.id)
    assert stored.full_name == "Nombre Actualizado"
    assert stored.email == EDITED_EMAIL
    assert stored.department_id == 2


def test_edit_employee_partial_update_exclude_unset(
    client: TestClient, auth_headers, admin, employee
) -> None:
    response = client.patch(
        f"/api/users/{employee.id}",
        headers=auth_headers(admin),
        json={"full_name": "Solo Nombre"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == "Solo Nombre"
    assert body["email"] == EMPLOYEE_EMAIL
    assert body["department_id"] == 1


def test_edit_employee_duplicate_email_returns_409(
    client: TestClient, auth_headers, admin, employee, user_factory
) -> None:
    user_factory(DUPLICATE_EMAIL)

    response = client.patch(
        f"/api/users/{employee.id}",
        headers=auth_headers(admin),
        json={"email": DUPLICATE_EMAIL},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


def test_edit_employee_duplicate_email_excluding_self_is_ok(
    client: TestClient, auth_headers, admin, employee
) -> None:
    response = client.patch(
        f"/api/users/{employee.id}",
        headers=auth_headers(admin),
        json={"email": employee.email},
    )

    assert response.status_code == 200


def test_edit_employee_nonexistent_department_returns_404(
    client: TestClient, auth_headers, admin, employee
) -> None:
    response = client.patch(
        f"/api/users/{employee.id}",
        headers=auth_headers(admin),
        json={"department_id": 99999},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_edit_employee_deactivated_returns_400(
    client: TestClient, auth_headers, admin, user_factory
) -> None:
    inactive = user_factory(SECOND_EMPLOYEE_EMAIL, is_active=False)

    response = client.patch(
        f"/api/users/{inactive.id}",
        headers=auth_headers(admin),
        json={"full_name": "No debería editarse"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "employee_inactive"


def test_edit_employee_self_downgrade_role_returns_400(
    client: TestClient, auth_headers, admin
) -> None:
    response = client.patch(
        f"/api/users/{admin.id}",
        headers=auth_headers(admin),
        json={"role": "EMPLOYEE"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "self_role_downgrade"


def test_edit_employee_not_found_returns_404(
    client: TestClient, auth_headers, admin
) -> None:
    response = client.patch(
        "/api/users/99999",
        headers=auth_headers(admin),
        json={"full_name": "Nada"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_edit_employee_non_admin_rejected_403(
    client: TestClient, auth_headers, admin, employee
) -> None:
    response = client.patch(
        f"/api/users/{admin.id}",
        headers=auth_headers(employee),
        json={"full_name": "Intento no admin"},
    )

    assert response.status_code == 403


def test_edit_employee_promoted_to_admin_clears_department(
    client: TestClient, auth_headers, admin, employee
) -> None:
    response = client.patch(
        f"/api/users/{employee.id}",
        headers=auth_headers(admin),
        json={"role": "ADMIN"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "ADMIN"
    assert body["department_id"] is None

    stored = _get_user(employee.id)
    assert stored.role == "ADMIN"
    assert stored.department_id is None


def test_edit_admin_to_employee_without_department_returns_400(
    client: TestClient, auth_headers, admin, user_factory
) -> None:
    target_admin = user_factory(SECOND_ADMIN_EMAIL, role="ADMIN", department_id=None)

    response = client.patch(
        f"/api/users/{target_admin.id}",
        headers=auth_headers(admin),
        json={"role": "EMPLOYEE"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "department_required"

    stored = _get_user(target_admin.id)
    assert stored.role == "ADMIN"
    assert stored.department_id is None


def test_edit_employee_with_null_department_returns_400(
    client: TestClient, auth_headers, admin, employee
) -> None:
    response = client.patch(
        f"/api/users/{employee.id}",
        headers=auth_headers(admin),
        json={"department_id": None},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "department_required"

    stored = _get_user(employee.id)
    assert stored.department_id == 1


def test_edit_employee_admin_with_department_returns_400(
    client: TestClient, auth_headers, admin, employee
) -> None:
    response = client.patch(
        f"/api/users/{employee.id}",
        headers=auth_headers(admin),
        json={"role": "ADMIN", "department_id": 1},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "admin_department_not_allowed"

    stored = _get_user(employee.id)
    assert stored.role == "EMPLOYEE"
    assert stored.department_id == 1


def test_edit_employee_email_is_normalized(
    client: TestClient, auth_headers, admin, employee
) -> None:
    response = client.patch(
        f"/api/users/{employee.id}",
        headers=auth_headers(admin),
        json={"email": f"  {EDITED_EMAIL.upper()}  "},
    )

    assert response.status_code == 200
    assert response.json()["email"] == EDITED_EMAIL

    stored = _get_user(employee.id)
    assert stored.email == EDITED_EMAIL
