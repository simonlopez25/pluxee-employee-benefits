from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError, ConflictError, NotFoundError
from app.core.security import hash_password, verify_password
from app.models.department import Department
from app.models.user import User
from app.schemas.auth import UserPublic
from app.schemas.user import ChangePasswordRequest, UserUpdateRequest


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


def update_employee(
    db: Session,
    user_id: int,
    current_user: User,
    payload: UserUpdateRequest,
) -> UserPublic:
    """Edita parcialmente un empleado (solo administrador).

    Validaciones:
    - El empleado debe existir (404).
    - No se puede editar un empleado ya dado de baja (400).
    - Un administrador no puede degradar su propio rol (400).
    - El email debe ser único excluyendo al propio empleado (409).
    - department_id debe existir si se envía (404).
    """
    user = _get_user_or_404(db, user_id)

    if not user.is_active:
        raise AppError(
            "Cannot edit a deactivated employee",
            status_code=400,
            code="employee_inactive",
        )

    update_data = payload.model_dump(exclude_unset=True)

    if "role" in update_data:
        _validate_role_change(current_user, user_id, update_data["role"])

    if "email" in update_data:
        _ensure_email_is_available(db, update_data["email"], exclude_id=user_id)

    if "department_id" in update_data and update_data["department_id"] is not None:
        _ensure_department_exists(db, update_data["department_id"])

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return UserPublic.model_validate(user)


def deactivate_employee(
    db: Session,
    user_id: int,
    current_user: User,
) -> UserPublic:
    """Da de baja lógica a un empleado (solo administrador).

    Validaciones:
    - El empleado debe existir (404).
    - No se puede dar de baja a uno mismo (400).
    - No se puede dar de baja a un empleado ya inactivo (400).
    """
    user = _get_user_or_404(db, user_id)

    if current_user.id == user_id:
        raise AppError(
            "Cannot deactivate yourself",
            status_code=400,
            code="self_deactivation",
        )

    if not user.is_active:
        raise AppError(
            "Employee is already deactivated",
            status_code=400,
            code="already_deactivated",
        )

    user.is_active = False
    user.deactivated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return UserPublic.model_validate(user)


def list_employees(db: Session) -> list[UserPublic]:
    """Lista todos los empleados ordenados por id (solo administrador)."""
    statement = select(User).order_by(User.id)
    users = list(db.scalars(statement).all())
    return [UserPublic.model_validate(user) for user in users]


def _get_user_or_404(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError("Employee not found")
    return user


def _validate_role_change(
    current_user: User, user_id: int, new_role: str
) -> None:
    if current_user.id == user_id and new_role != "ADMIN":
        raise AppError(
            "An administrator cannot downgrade their own role",
            status_code=400,
            code="self_role_downgrade",
        )


def _ensure_email_is_available(
    db: Session, email: str, *, exclude_id: int
) -> None:
    statement = select(User.id).where(
        User.email == email,
        User.id != exclude_id,
    )
    if db.scalar(statement) is not None:
        raise ConflictError("Email already in use")


def _ensure_department_exists(db: Session, department_id: int) -> None:
    department = db.get(Department, department_id)
    if department is None:
        raise NotFoundError("Department not found")
