from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, UserPublic


def login(db: Session, data: LoginRequest) -> LoginResponse:
    email = data.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))

    if user is None or not verify_password(data.password, user.password_hash):
        raise AppError(
            "Correo o contraseña incorrectos",
            status_code=401,
            code="invalid_credentials",
        )
    if not user.is_active:
        raise AppError(
            "Tu cuenta está desactivada. Contacta con administración",
            status_code=403,
            code="account_inactive",
        )

    return LoginResponse(
        access_token=create_access_token(user.id, user.role),
        expires_in=settings.jwt_expires_minutes * 60,
        user=UserPublic.model_validate(user),
    )