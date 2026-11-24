"""Tests de PATCH /api/users/me/password y GET /api/me (HU-05 / PEB-39)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import verify_password
from app.models.user import User

TEST_EMAIL = "test-password@pluxee.test"
TEST_PASSWORD = "Prueba123!"
NEW_PASSWORD = "NuevaContrasena123!"


@pytest.fixture(autouse=True)
def cleanup(delete_users):
    delete_users(TEST_EMAIL)
    yield
    delete_users(TEST_EMAIL)


def _create_user(user_factory) -> User:
    return user_factory(
        TEST_EMAIL,
        full_name="Password Test User",
        must_change_password=False,
    )


def _stored_user() -> User | None:
    with SessionLocal() as db:
        return db.scalar(select(User).where(User.email == TEST_EMAIL))


def test_change_password_returns_200_and_updates_user(
    client: TestClient, auth_headers, user_factory
) -> None:
    user = _create_user(user_factory)

    response = client.patch(
        "/api/users/me/password",
        headers=auth_headers(user),
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

    stored = _stored_user()
    assert stored is not None
    assert stored.must_change_password is False
    assert verify_password(NEW_PASSWORD, stored.password_hash) is True
    assert verify_password(TEST_PASSWORD, stored.password_hash) is False


def test_change_password_with_wrong_current_password_returns_400(
    client: TestClient, auth_headers, user_factory
) -> None:
    user = _create_user(user_factory)

    response = client.patch(
        "/api/users/me/password",
        headers=auth_headers(user),
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


def test_change_password_with_short_new_password_returns_422(
    client: TestClient, auth_headers, user_factory
) -> None:
    user = _create_user(user_factory)

    response = client.patch(
        "/api/users/me/password",
        headers=auth_headers(user),
        json={
            "current_password": TEST_PASSWORD,
            "new_password": "corta",
            "confirm_password": "corta",
        },
    )

    assert response.status_code == 422


def test_change_password_with_mismatched_confirmation_returns_422(
    client: TestClient, auth_headers, user_factory
) -> None:
    user = _create_user(user_factory)

    response = client.patch(
        "/api/users/me/password",
        headers=auth_headers(user),
        json={
            "current_password": TEST_PASSWORD,
            "new_password": NEW_PASSWORD,
            "confirm_password": "OtraContrasena123!",
        },
    )

    assert response.status_code == 422


def test_change_password_with_same_as_current_returns_422(
    client: TestClient, auth_headers, user_factory
) -> None:
    user = _create_user(user_factory)

    response = client.patch(
        "/api/users/me/password",
        headers=auth_headers(user),
        json={
            "current_password": TEST_PASSWORD,
            "new_password": TEST_PASSWORD,
            "confirm_password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 422


def test_change_password_without_token_returns_401(client: TestClient) -> None:
    response = client.patch(
        "/api/users/me/password",
        json={
            "current_password": TEST_PASSWORD,
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD,
        },
    )

    assert response.status_code == 401


def test_me_with_valid_token_returns_200(
    client: TestClient, auth_headers, user_factory
) -> None:
    user = _create_user(user_factory)

    response = client.get("/api/me", headers=auth_headers(user))

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == TEST_EMAIL
    assert body["must_change_password"] is False


def test_me_without_token_returns_401(client: TestClient) -> None:
    response = client.get("/api/me")
    assert response.status_code == 401
