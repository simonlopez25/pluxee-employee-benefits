from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.user import User
from app.schemas.auth import UserPublic
from app.schemas.user import ChangePasswordRequest, UserCreate, UserUpdateRequest
from app.services import user_service

router = APIRouter(tags=["users"])


@router.get(
    "/users",
    response_model=list[UserPublic],
    summary="Lista los usuarios (admin)",
)
def list_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[UserPublic]:
    return user_service.list_users(db)


@router.post(
    "/users",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Da de alta a un empleado (admin)",
)
def register_employee(
    payload: UserCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserPublic:
    return user_service.create_employee(db, payload)


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
    return user_service.deactivate_employee(db, user_id, admin)
