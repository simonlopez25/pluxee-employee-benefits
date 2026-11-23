"""Endpoints de gestión de empleados: edición y baja lógica (solo administrador)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.user import User
from app.schemas.auth import UserPublic
from app.schemas.user import ChangePasswordRequest, UserUpdateRequest
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


UserIdPath = Annotated[int, Path(description="Id del empleado")]


@router.patch(
    "/users/{user_id}",
    response_model=UserPublic,
    status_code=status.HTTP_200_OK,
    summary="Edita un empleado (admin)",
)
def update_employee(
    user_id: UserIdPath,
    payload: UserUpdateRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserPublic:
    """Actualiza parcialmente los datos de un empleado."""
    return user_service.update_employee(db, user_id, admin, payload)


@router.patch(
    "/users/{user_id}/deactivate",
    response_model=UserPublic,
    status_code=status.HTTP_200_OK,
    summary="Da de baja lógica a un empleado (admin)",
)
def deactivate_employee(
    user_id: UserIdPath,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserPublic:
    """Marca a un empleado como inactivo (is_active=False) con fecha de baja."""
    return user_service.deactivate_employee(db, user_id, admin)
