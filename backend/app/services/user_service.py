from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.auth import UserPublic
from app.schemas.user import ChangePasswordRequest


def change_password(
    db: Session, user: User, data: ChangePasswordRequest
) -> UserPublic:
    if not verify_password(data.current_password, user.password_hash):
        raise AppError(
            "La contraseña actual no es correcta",
            status_code=400,
            code="invalid_current_password",
        )

    user.password_hash = hash_password(data.new_password)
    user.must_change_password = False
    db.commit()
    db.refresh(user)
    return UserPublic.model_validate(user)
