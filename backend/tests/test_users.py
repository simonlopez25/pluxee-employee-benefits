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
