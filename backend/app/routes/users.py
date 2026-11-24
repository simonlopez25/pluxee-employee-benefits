"""Endpoints de gestión de usuarios: alta, edición y baja lógica."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import ConflictError, NotFoundError
from app.core.security import get_current_user, hash_password, require_admin
from app.models.department import Department
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
    """Devuelve la lista de usuarios (administradores y empleados) con su estado de activación."""
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
    """Crea una cuenta de empleado con grupo, contraseña temporal y cambio obligatorio."""
    if db.scalar(
        select(User.id).where(User.email == payload.email)
    ) is not None:
        raise ConflictError("Ya existe un usuario con ese correo electrónico")

    if db.get(Department, payload.department_id) is None:
        raise NotFoundError("El departamento no existe")

    user = User(
        email=payload.email,
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.temporary_password),
        department_id=payload.department_id,
        role="EMPLOYEE",
        is_active=True,
        must_change_password=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserPublic.model_validate(user)


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
