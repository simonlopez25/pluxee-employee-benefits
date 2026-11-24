import pytest
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import create_access_token, get_current_user
from app.main import app
from app.models.user import User


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
    if request.node.fspath.basename == "test_users.py":
        yield
        return
    # Los tests existentes no envían token: por defecto todo pasa como ADMIN
    user = _seed_user("ADMIN")
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def real_auth():
    saved = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()
    app.dependency_overrides.update(saved)


@pytest.fixture()
def admin_headers():
    user = _seed_user("ADMIN")
    return {"Authorization": f"Bearer {create_access_token(user.id, user.role)}"}


@pytest.fixture()
def employee_headers():
    user = _seed_user("EMPLOYEE")
    return {"Authorization": f"Bearer {create_access_token(user.id, user.role)}"}