"""Endpoint de autenticación: POST /api/login."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, UserPublic
from app.services import auth as auth_service

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=LoginResponse, summary="Login")
def login(data: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """Valida las credenciales y devuelve un JWT."""
    return auth_service.login(db, data)


@router.get("/me", response_model=UserPublic, summary="Sesión actual")
def me(user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic.model_validate(user)