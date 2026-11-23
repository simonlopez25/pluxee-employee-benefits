"""Endpoint de gestión del usuario autenticado."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.auth import UserPublic
from app.schemas.user import ChangePasswordRequest
from app.services import user_service

router = APIRouter(tags=["users"])


@router.patch(
    "/users/me/password", response_model=UserPublic, summary="Cambiar contraseña"
)
def change_password(
    data: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserPublic:
    return user_service.change_password(db, user, data)
