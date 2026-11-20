"""Integration tests for POST /api/users employee registration (PEB-15 / HU-07)."""

from __future__ import annotations

from collections.abc import Generator
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import verify_password
from app.main import app
from app.models.department import Department
from app.models.user import User


@pytest.fixture()
def session_factory() -> Generator[sessionmaker[Session], None, None]:
    """Create an isolated in-memory SQLite database for user registration tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Only create tables needed by this test module; unrelated tables use PostgreSQL-specific CHECKs.
    Base.metadata.create_all(
        bind=engine,
        tables=[Department.__table__, User.__table__],
    )

    testing_session_local = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    @event.listens_for(testing_session_local, "before_flush")
    def _populate_created_at(session: Session, _flush_context, _instances) -> None:
        # SQLite treats server_default="NOW()" as a literal string rather than a timestamp.
        for obj in session.new:
            if hasattr(obj, "created_at") and obj.created_at is None:
                obj.created_at = datetime.now(timezone.utc)

    try:
        yield testing_session_local
    finally:
        engine.dispose()


@pytest.fixture()
def seeded_departments(session_factory: sessionmaker[Session]) -> dict[str, int]:
    """Seed one active and one inactive department for each test."""
    with session_factory() as db:
        active_dept = Department(name="Engineering", currency="EUR", is_active=True)
        inactive_dept = Department(name="Legacy Ops", currency="EUR", is_active=False)
        db.add_all([active_dept, inactive_dept])
        db.commit()
        db.refresh(active_dept)
        db.refresh(inactive_dept)
        return {"active": active_dept.id, "inactive": inactive_dept.id}


@pytest.fixture()
def client(
    session_factory: sessionmaker[Session],
    seeded_departments: dict[str, int],
) -> Generator[TestClient, None, None]:
    """Provide a TestClient wired to the isolated in-memory database session."""

    def _override_get_db() -> Generator[Session, None, None]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def db_session(session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    """Provide a database session for post-request persistence assertions."""
    with session_factory() as db:
        yield db


def test_register_employee_created_and_security_defaults(
    client: TestClient,
    db_session: Session,
    seeded_departments: dict[str, int],
) -> None:
    """POST /api/users creates an employee with normalized data and hashed password."""
    response = client.post(
        "/api/users",
        json={
            "email": "Alice.Smith@Pluxee.com",
            "full_name": "  Alice Smith  ",
            "temporary_password": "TempPassword123!",
            "department_id": seeded_departments["active"],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert isinstance(body["id"], int)
    assert body["email"] == "alice.smith@pluxee.com"
    assert body["full_name"] == "Alice Smith"
    assert body["role"] == "EMPLOYEE"
    assert body["department_id"] == seeded_departments["active"]
    assert body["is_active"] is True
    assert body["must_change_password"] is True
    assert body["created_at"]
    assert "password_hash" not in body
    assert "temporary_password" not in body
    assert "password" not in body

    stored_user = (
        db_session.query(User)
        .filter(User.email == "alice.smith@pluxee.com")
        .first()
    )
    assert stored_user is not None
    assert stored_user.password_hash != "TempPassword123!"
    assert stored_user.password_hash.startswith("$2b$")
    assert verify_password("TempPassword123!", stored_user.password_hash) is True
    assert verify_password("WrongPass!", stored_user.password_hash) is False
    assert stored_user.role == "EMPLOYEE"
    assert stored_user.is_active is True
    assert stored_user.must_change_password is True


def test_register_employee_duplicate_email_returns_409(
    client: TestClient,
    seeded_departments: dict[str, int],
) -> None:
    """POST /api/users rejects duplicate emails case-insensitively with 409 Conflict."""
    first = client.post(
        "/api/users",
        json={
            "email": "duplicate@pluxee.com",
            "full_name": "First Employee",
            "temporary_password": "TempPassword123!",
            "department_id": seeded_departments["active"],
        },
    )
    assert first.status_code == 201

    second = client.post(
        "/api/users",
        json={
            "email": "DUPLICATE@pluxee.com",
            "full_name": "Second Employee",
            "temporary_password": "TempPassword123!",
            "department_id": seeded_departments["active"],
        },
    )
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "USER_EMAIL_ALREADY_EXISTS"


def test_register_employee_nonexistent_department_returns_404(
    client: TestClient,
) -> None:
    """POST /api/users returns 404 Not Found when department_id does not exist."""
    response = client.post(
        "/api/users",
        json={
            "email": "missing.dept@pluxee.com",
            "full_name": "Missing Dept Employee",
            "temporary_password": "TempPassword123!",
            "department_id": 99999,
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DEPARTMENT_NOT_FOUND"


def test_register_employee_inactive_department_returns_404(
    client: TestClient,
    seeded_departments: dict[str, int],
) -> None:
    """POST /api/users returns 404 Not Found when the target department is inactive."""
    response = client.post(
        "/api/users",
        json={
            "email": "inactive.dept@pluxee.com",
            "full_name": "Inactive Dept Employee",
            "temporary_password": "TempPassword123!",
            "department_id": seeded_departments["inactive"],
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DEPARTMENT_NOT_FOUND"


def test_register_employee_invalid_payload_returns_422(
    client: TestClient,
    seeded_departments: dict[str, int],
) -> None:
    """POST /api/users rejects short temporary passwords and invalid email formats with 422."""
    short_password_resp = client.post(
        "/api/users",
        json={
            "email": "valid.user@pluxee.com",
            "full_name": "Valid User",
            "temporary_password": "short",
            "department_id": seeded_departments["active"],
        },
    )
    assert short_password_resp.status_code == 422

    invalid_email_resp = client.post(
        "/api/users",
        json={
            "email": "not-an-email",
            "full_name": "Valid User",
            "temporary_password": "TempPassword123!",
            "department_id": seeded_departments["active"],
        },
    )
    assert invalid_email_resp.status_code == 422
