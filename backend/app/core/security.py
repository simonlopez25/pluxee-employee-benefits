from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.errors import AppError
from app.models.user import User

_bearer = HTTPBearer(auto_error=False)


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode(
        "utf-8"
    )


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user_id: int, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(
            (now + timedelta(minutes=settings.jwt_expires_minutes)).timestamp()
        ),
    }
    return jwt.encode(
        payload, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except jwt.ExpiredSignatureError as exc:
        raise AppError(
            "La sesión ha caducado. Vuelve a iniciar sesión",
            status_code=401,
            code="token_expired",
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise AppError("Sesión no válida", status_code=401, code="invalid_token") from exc


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AppError(
            "Autenticación requerida", status_code=401, code="missing_token"
        )

    payload = _decode_token(credentials.credentials)

    sub = payload.get("sub")
    try:
        user_id = int(sub)
    except (TypeError, ValueError) as exc:
        raise AppError("Sesión no válida", status_code=401, code="invalid_token") from exc

    user = db.get(User, user_id)
    if user is None:
        raise AppError("Sesión no válida", status_code=401, code="invalid_token")
    if not user.is_active:
        raise AppError(
            "Tu cuenta está desactivada. Contacta con administración",
            status_code=403,
            code="account_inactive",
        )
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "ADMIN":
        raise AppError(
            "No tienes permisos para esta acción",
            status_code=403,
            code="forbidden_role",
        )
    return user