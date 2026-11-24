"""Fixtures compartidas de los tests."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import create_access_token, get_current_user, hash_password
from app.main import app
from app.models.user import User

TEST_PASSWORD = "Prueba123!"


def _seed_user(role: str) -> User:
    db = SessionLocal()
    try:
        user = db.scalar(
            select(User).where(User.role == role, User.is_active.is_(True)).limit(1)
        )
    finally:
        db.close()
    assert user is not None, f"No hay usuario {role} activo en la BD (¿falta el seed?)"
    return user


@pytest.fixture(autouse=True)
def _act_as_admin_by_default(request):
    """Por defecto, todos los tests pasan como ADMIN salvo test_users.py"""
    if request.node.fspath.basename == "test_users.py":
        yield
        return
    user = _seed_user("ADMIN")
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def real_auth():
    """Limpia los overrides para tests que necesitan autenticación real"""
    saved = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()
    app.dependency_overrides.update(saved)


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def admin_headers():
    user = _seed_user("ADMIN")
    return {"Authorization": f"Bearer {create_access_token(user.id, user.role)}"}


@pytest.fixture()
def employee_headers():
    user = _seed_user("EMPLOYEE")
    return {"Authorization": f"Bearer {create_access_token(user.id, user.role)}"}


@pytest.fixture()
def auth_headers() -> Callable[[User], dict[str, str]]:
    def _headers(user: User) -> dict[str, str]:
        token = create_access_token(user.id, user.role)
        return {"Authorization": f"Bearer {token}"}
    return _headers


@pytest.fixture()
def user_factory() -> Callable[..., User]:
    def _create(
        email: str,
        *,
        full_name: str = "Test User",
        role: str = "EMPLOYEE",
        department_id: int | None = 1,
        is_active: bool = True,
        must_change_password: bool = False,
    ) -> User:
        with SessionLocal() as db:
            user = User(
                full_name=full_name,
                email=email,
                password_hash=hash_password(TEST_PASSWORD),
                role=role,
                department_id=department_id,
                must_change_password=must_change_password,
                is_active=is_active,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
    return _create


@pytest.fixture()
def delete_users() -> Callable[..., None]:
    def _delete(*emails: str) -> None:
        with SessionLocal() as db:
            for email in emails:
                user = db.scalar(select(User).where(User.email == email))
                if user:
                    db.delete(user)
            db.commit()
    return _delete