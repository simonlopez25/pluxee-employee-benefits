from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.models.user import User

ADMIN_EMAIL = "test-admin-peb16@pluxee.test"
EMPLOYEE_EMAIL = "test-employee-peb16@pluxee.test"

TEST_USER_EMAILS = (ADMIN_EMAIL, EMPLOYEE_EMAIL)


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


def test_deactivate_employee_success_sets_flags(
    client: TestClient, auth_headers, admin, employee
) -> None:
    response = client.patch(
        f"/api/users/{employee.id}/deactivate",
        headers=auth_headers(admin),
    )

    assert response.status_code == 200
    assert response.json()["id"] == employee.id

    stored = _get_user(employee.id)
    assert stored.is_active is False
    assert stored.deactivated_at is not None


def test_deactivate_employee_self_blocked_400(
    client: TestClient, auth_headers, admin
) -> None:
    response = client.patch(
        f"/api/users/{admin.id}/deactivate",
        headers=auth_headers(admin),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "self_deactivation"
    assert _get_user(admin.id).is_active is True


def test_deactivate_employee_already_inactive_400(
    client: TestClient, auth_headers, admin, user_factory
) -> None:
    inactive = user_factory(EMPLOYEE_EMAIL, is_active=False)

    response = client.patch(
        f"/api/users/{inactive.id}/deactivate",
        headers=auth_headers(admin),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "already_deactivated"


def test_deactivate_employee_not_found_404(
    client: TestClient, auth_headers, admin
) -> None:
    response = client.patch(
        "/api/users/99999/deactivate",
        headers=auth_headers(admin),
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_deactivate_employee_non_admin_rejected_403(
    client: TestClient, auth_headers, admin, employee
) -> None:
    response = client.patch(
        f"/api/users/{employee.id}/deactivate",
        headers=auth_headers(employee),
    )

    assert response.status_code == 403


def test_deactivated_employee_loses_immediate_access(
    client: TestClient, auth_headers, admin, employee
) -> None:
    employee_headers = auth_headers(employee)
    assert client.get("/api/me", headers=employee_headers).status_code == 200

    response = client.patch(
        f"/api/users/{employee.id}/deactivate",
        headers=auth_headers(admin),
    )
    assert response.status_code == 200

    after = client.get("/api/me", headers=employee_headers)
    assert after.status_code == 403
    assert after.json()["error"]["code"] == "account_inactive"


def test_deactivated_employee_cannot_login(
    client: TestClient, auth_headers, admin, employee
) -> None:
    client.patch(
        f"/api/users/{employee.id}/deactivate",
        headers=auth_headers(admin),
    )

    response = client.post(
        "/api/login",
        json={"email": EMPLOYEE_EMAIL, "password": "Prueba123!"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "account_inactive"
