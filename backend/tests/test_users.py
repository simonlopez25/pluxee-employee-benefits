"""Tests del endpoint PATCH /api/users/me/password (HU-05 / PEB-39)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.user import User

client = TestClient(app)

TEST_EMAIL = "test-password@pluxee.test"
TEST_PASSWORD = "Prueba123!"
NEW_PASSWORD = "NuevaContrasena123!"


def _get_user(db: SessionLocal, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def _create_test_user(db: SessionLocal) -> User:
    """Crea un usuario de prueba con must_change_password=False."""
    user = User(
        full_name="Password Test User",
        email=TEST_EMAIL,
        password_hash=hash_password(TEST_PASSWORD),
        role="EMPLOYEE",
        department_id=1,
        must_change_password=False,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _delete_test_user() -> None:
    with SessionLocal() as db:
        user = _get_user(db, TEST_EMAIL)
        if user:
            db.delete(user)
            db.commit()


@pytest.fixture(autouse=True)
def cleanup():
    _delete_test_user()
    yield
    _delete_test_user()


def _auth_headers(user: User) -> dict[str, str]:
    token = create_access_token(user.id, user.role)
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------
# 1. Cambio correcto → 200, must_change_password=False, body actualizado
# ---------------------------------------------------------------------
def test_change_password_returns_200_and_updates_user() -> None:
    user = None
    with SessionLocal() as db:
        user = _create_test_user(db)

    response = client.patch(
        "/api/users/me/password",
        headers=_auth_headers(user),
        json={
            "current_password": TEST_PASSWORD,
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == TEST_EMAIL
    assert body["must_change_password"] is False

    # Verificar en BD que la contraseña se ha actualizado
    with SessionLocal() as db:
        stored = _get_user(db, TEST_EMAIL)
        assert stored is not None
        assert stored.must_change_password is False
        # La nueva contraseña debe coincidir (bcrypt)
        from app.core.security import verify_password

        assert verify_password(NEW_PASSWORD, stored.password_hash) is True
        # La vieja ya no debe funcionar
        assert verify_password(TEST_PASSWORD, stored.password_hash) is False


# ---------------------------------------------------------------------
# 2. Contraseña actual incorrecta → 400 (no 401)
# ---------------------------------------------------------------------
def test_change_password_with_wrong_current_password_returns_400() -> None:
    user = None
    with SessionLocal() as db:
        user = _create_test_user(db)

    response = client.patch(
        "/api/users/me/password",
        headers=_auth_headers(user),
        json={
            "current_password": "wrongpassword",
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD,
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "invalid_current_password"
    assert "contraseña actual" in body["error"]["message"].lower()


# ---------------------------------------------------------------------
# 3. Validaciones de schema → 422
# ---------------------------------------------------------------------
def test_change_password_with_short_new_password_returns_422() -> None:
    user = None
    with SessionLocal() as db:
        user = _create_test_user(db)

    response = client.patch(
        "/api/users/me/password",
        headers=_auth_headers(user),
        json={
            "current_password": TEST_PASSWORD,
            "new_password": "corta",
            "confirm_password": "corta",
        },
    )

    assert response.status_code == 422


def test_change_password_with_mismatched_confirmation_returns_422() -> None:
    user = None
    with SessionLocal() as db:
        user = _create_test_user(db)

    response = client.patch(
        "/api/users/me/password",
        headers=_auth_headers(user),
        json={
            "current_password": TEST_PASSWORD,
            "new_password": NEW_PASSWORD,
            "confirm_password": "OtraContrasena123!",
        },
    )

    assert response.status_code == 422


def test_change_password_with_same_as_current_returns_422() -> None:
    user = None
    with SessionLocal() as db:
        user = _create_test_user(db)

    response = client.patch(
        "/api/users/me/password",
        headers=_auth_headers(user),
        json={
            "current_password": TEST_PASSWORD,
            "new_password": TEST_PASSWORD,
            "confirm_password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------
# 4. Sin token → 401 (sesión caducada)
# ---------------------------------------------------------------------
def test_change_password_without_token_returns_401() -> None:
    response = client.patch(
        "/api/users/me/password",
        json={
            "current_password": TEST_PASSWORD,
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD,
        },
    )

    assert response.status_code == 401


# ---------------------------------------------------------------------
# 5. GET /me con token válido → 200, sin token → 401
# ---------------------------------------------------------------------
def test_me_with_valid_token_returns_200() -> None:
    user = None
    with SessionLocal() as db:
        user = _create_test_user(db)

    response = client.get("/api/me", headers=_auth_headers(user))

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == TEST_EMAIL
    assert body["must_change_password"] is False


def test_me_without_token_returns_401() -> None:
    response = client.get("/api/me")
    assert response.status_code == 401


# ---------------------------------------------------------------------
# PEB-16 / HU-08: Edición y baja lógica de empleados
# ---------------------------------------------------------------------

ADMIN_EMAIL = "test-admin-peb16@pluxee.test"
SECOND_ADMIN_EMAIL = "test-admin2-peb16@pluxee.test"
EMPLOYEE_EMAIL = "test-employee-peb16@pluxee.test"
SECOND_EMPLOYEE_EMAIL = "test-employee2-peb16@pluxee.test"
DUPLICATE_EMAIL_EMAIL = "test-duplicate-peb16@pluxee.test"
EDITED_EMAIL_EMAIL = "edited.employee-peb16@pluxee.test"


def _create_admin(db: SessionLocal, email: str = ADMIN_EMAIL) -> User:
    user = User(
        full_name="Test Admin",
        email=email,
        password_hash=hash_password("Prueba123!"),
        role="ADMIN",
        department_id=None,
        must_change_password=False,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _create_employee(
    db: SessionLocal,
    email: str = EMPLOYEE_EMAIL,
    department_id: int = 1,
    is_active: bool = True,
) -> User:
    user = User(
        full_name="Test Employee",
        email=email,
        password_hash=hash_password("Prueba123!"),
        role="EMPLOYEE",
        department_id=department_id,
        must_change_password=False,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _delete_test_users() -> None:
    with SessionLocal() as db:
        for email in (
            ADMIN_EMAIL,
            SECOND_ADMIN_EMAIL,
            EMPLOYEE_EMAIL,
            SECOND_EMPLOYEE_EMAIL,
            DUPLICATE_EMAIL_EMAIL,
            EDITED_EMAIL_EMAIL,
            EDITED_EMAIL_EMAIL.upper(),
        ):
            user = db.scalar(select(User).where(User.email == email))
            if user:
                db.delete(user)
        db.commit()


@pytest.fixture(autouse=True)
def cleanup_peb16_users():
    _delete_test_users()
    yield
    _delete_test_users()


# ---------------------------------------------------------------------
# PATCH /api/users/{user_id} — Edición de empleado
# ---------------------------------------------------------------------

def test_edit_employee_success_updates_fields() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)
        employee = _create_employee(db)

    token = create_access_token(admin.id, admin.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        f"/api/users/{employee.id}",
        headers=headers,
        json={
            "full_name": "Nombre Actualizado",
            "email": EDITED_EMAIL_EMAIL,
            "department_id": 2,
            "role": "EMPLOYEE",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == employee.id
    assert body["full_name"] == "Nombre Actualizado"
    assert body["email"] == EDITED_EMAIL_EMAIL
    assert body["department_id"] == 2
    assert body["role"] == "EMPLOYEE"

    with SessionLocal() as db:
        stored = db.get(User, employee.id)
        assert stored.full_name == "Nombre Actualizado"
        assert stored.email == EDITED_EMAIL_EMAIL
        assert stored.department_id == 2


def test_edit_employee_partial_update_exclude_unset() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)
        employee = _create_employee(db)

    token = create_access_token(admin.id, admin.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        f"/api/users/{employee.id}",
        headers=headers,
        json={"full_name": "Solo Nombre"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == "Solo Nombre"
    assert body["email"] == EMPLOYEE_EMAIL  # no se envió, no cambia
    assert body["department_id"] == 1  # no se envió, no cambia


def test_edit_employee_duplicate_email_returns_409() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)
        employee = _create_employee(db)
        _create_employee(db, email=DUPLICATE_EMAIL_EMAIL)

    token = create_access_token(admin.id, admin.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        f"/api/users/{employee.id}",
        headers=headers,
        json={"email": DUPLICATE_EMAIL_EMAIL},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


def test_edit_employee_duplicate_email_excluding_self_is_ok() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)
        employee = _create_employee(db)

    token = create_access_token(admin.id, admin.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        f"/api/users/{employee.id}",
        headers=headers,
        json={"email": employee.email},  # mismo email, debe permitir
    )

    assert response.status_code == 200


def test_edit_employee_nonexistent_department_returns_404() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)
        employee = _create_employee(db)

    token = create_access_token(admin.id, admin.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        f"/api/users/{employee.id}",
        headers=headers,
        json={"department_id": 99999},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_edit_employee_deactivated_returns_400() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)
        employee = _create_employee(db, is_active=False)

    token = create_access_token(admin.id, admin.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        f"/api/users/{employee.id}",
        headers=headers,
        json={"full_name": "No debería editarse"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "employee_inactive"


def test_edit_employee_self_downgrade_role_returns_400() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)

    token = create_access_token(admin.id, admin.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        f"/api/users/{admin.id}",
        headers=headers,
        json={"role": "EMPLOYEE"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "self_role_downgrade"


def test_edit_employee_not_found_returns_404() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)

    token = create_access_token(admin.id, admin.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        "/api/users/99999",
        headers=headers,
        json={"full_name": "Nada"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_edit_employee_non_admin_rejected_403() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)
        employee = _create_employee(db)

    token = create_access_token(employee.id, employee.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        f"/api/users/{admin.id}",
        headers=headers,
        json={"full_name": "Intento no admin"},
    )

    assert response.status_code == 403


# ---------------------------------------------------------------------
# ck_users_role_department: el estado final rol/departamento no puede
# estallar en un IntegrityError/500
# ---------------------------------------------------------------------

def test_edit_employee_promoted_to_admin_clears_department() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)
        employee = _create_employee(db)

    token = create_access_token(admin.id, admin.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        f"/api/users/{employee.id}",
        headers=headers,
        json={"role": "ADMIN"},  # sin department_id: debe limpiarse solo
    )

    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "ADMIN"
    assert body["department_id"] is None

    with SessionLocal() as db:
        stored = db.get(User, employee.id)
        assert stored.role == "ADMIN"
        assert stored.department_id is None


def test_edit_admin_to_employee_without_department_returns_400() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)
        target_admin = _create_admin(db, email=SECOND_ADMIN_EMAIL)

    token = create_access_token(admin.id, admin.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        f"/api/users/{target_admin.id}",
        headers=headers,
        json={"role": "EMPLOYEE"},  # sin department_id: violaría el CHECK
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "department_required"

    with SessionLocal() as db:
        stored = db.get(User, target_admin.id)
        assert stored.role == "ADMIN"
        assert stored.department_id is None


def test_edit_employee_with_null_department_returns_400() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)
        employee = _create_employee(db)

    token = create_access_token(admin.id, admin.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        f"/api/users/{employee.id}",
        headers=headers,
        json={"department_id": None},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "department_required"

    with SessionLocal() as db:
        stored = db.get(User, employee.id)
        assert stored.department_id == 1


def test_edit_employee_admin_with_department_returns_400() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)
        employee = _create_employee(db)

    token = create_access_token(admin.id, admin.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        f"/api/users/{employee.id}",
        headers=headers,
        json={"role": "ADMIN", "department_id": 1},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "admin_department_not_allowed"

    with SessionLocal() as db:
        stored = db.get(User, employee.id)
        assert stored.role == "EMPLOYEE"
        assert stored.department_id == 1


def test_edit_employee_email_is_normalized() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)
        employee = _create_employee(db)

    token = create_access_token(admin.id, admin.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        f"/api/users/{employee.id}",
        headers=headers,
        json={"email": f"  {EDITED_EMAIL_EMAIL.upper()}  "},
    )

    assert response.status_code == 200
    assert response.json()["email"] == EDITED_EMAIL_EMAIL

    with SessionLocal() as db:
        stored = db.get(User, employee.id)
        assert stored.email == EDITED_EMAIL_EMAIL


# ---------------------------------------------------------------------
# PATCH /api/users/{user_id}/deactivate — Baja lógica
# ---------------------------------------------------------------------

def test_deactivate_employee_success_sets_flags() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)
        employee = _create_employee(db)

    token = create_access_token(admin.id, admin.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        f"/api/users/{employee.id}/deactivate",
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == employee.id

    with SessionLocal() as db:
        stored = db.get(User, employee.id)
        assert stored.is_active is False
        assert stored.deactivated_at is not None

    # El registro sigue en la BD: baja lógica, sin DELETE físico
    assert db.get(User, employee.id) is not None


def test_deactivate_employee_self_blocked_400() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)

    token = create_access_token(admin.id, admin.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        f"/api/users/{admin.id}/deactivate",
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "self_deactivation"

    # Sigue activo
    with SessionLocal() as db:
        stored = db.get(User, admin.id)
        assert stored.is_active is True


def test_deactivate_employee_already_inactive_400() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)
        employee = _create_employee(db, is_active=False)

    token = create_access_token(admin.id, admin.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        f"/api/users/{employee.id}/deactivate",
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "already_deactivated"


def test_deactivate_employee_not_found_404() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)

    token = create_access_token(admin.id, admin.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        "/api/users/99999/deactivate",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_deactivate_employee_non_admin_rejected_403() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)
        employee = _create_employee(db)

    token = create_access_token(employee.id, employee.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        f"/api/users/{employee.id}/deactivate",
        headers=headers,
    )

    assert response.status_code == 403


# ---------------------------------------------------------------------
# Revocación de acceso inmediata tras baja lógica
# ---------------------------------------------------------------------

def test_deactivated_employee_loses_immediate_access() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)
        employee = _create_employee(db)

    # Token válido antes de la baja
    token_before = create_access_token(employee.id, employee.role)
    headers_before = {"Authorization": f"Bearer {token_before}"}
    response_before = client.get("/api/me", headers=headers_before)
    assert response_before.status_code == 200

    # Dar de baja como administrador
    admin_token = create_access_token(admin.id, admin.role)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    deactivate_response = client.patch(
        f"/api/users/{employee.id}/deactivate",
        headers=admin_headers,
    )
    assert deactivate_response.status_code == 200

    # El mismo token ya no da acceso (get_current_user rechaza is_active=False)
    response_after = client.get("/api/me", headers=headers_before)
    assert response_after.status_code == 403
    assert response_after.json()["error"]["code"] == "account_inactive"


def test_deactivated_employee_cannot_login() -> None:
    with SessionLocal() as db:
        admin = _create_admin(db)
        employee = _create_employee(db)

    admin_token = create_access_token(admin.id, admin.role)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    client.patch(
        f"/api/users/{employee.id}/deactivate",
        headers=admin_headers,
    )

    login_response = client.post(
        "/api/login",
        json={"email": EMPLOYEE_EMAIL, "password": "Prueba123!"},
    )
    assert login_response.status_code == 403
    assert login_response.json()["error"]["code"] == "account_inactive"
