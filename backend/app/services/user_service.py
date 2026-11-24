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
    """Edita parcialmente un empleado (solo administrador)."""
    user = _get_user_or_404(db, user_id)

    if not user.is_active:
        raise AppError(
            "No se puede editar un empleado dado de baja",
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

    update_data = _validate_and_normalize_role_department(update_data, user)

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
    """Da de baja lógica a un empleado (solo administrador)."""
    user = _get_user_or_404(db, user_id)

    if current_user.id == user_id:
        raise AppError(
            "No puedes darte de baja a ti mismo",
            status_code=400,
            code="self_deactivation",
        )

    if not user.is_active:
        raise AppError(
            "El empleado ya está dado de baja",
            status_code=400,
            code="already_deactivated",
        )

    user.is_active = False
    user.deactivated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return UserPublic.model_validate(user)


def list_users(db: Session) -> list[UserPublic]:
    """Lista todos los usuarios (administradores y empleados) ordenados por identificador."""
    statement = select(User).order_by(User.id)
    users = list(db.scalars(statement).all())
    return [UserPublic.model_validate(user) for user in users]


def _get_user_or_404(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError("El empleado no existe")
    return user


def _validate_role_change(
    current_user: User, user_id: int, new_role: str
) -> None:
    if current_user.id == user_id and new_role != "ADMIN":
        raise AppError(
            "Un administrador no puede rebajar su propio rol",
            status_code=400,
            code="self_role_downgrade",
        )


def _validate_and_normalize_role_department(
    update_data: dict, user: User
) -> dict:
    """Valida y normaliza la combinación final rol/departamento."""
    final_role = update_data.get("role", user.role)

    if final_role == "ADMIN":
        if "department_id" in update_data and update_data["department_id"] is not None:
            raise AppError(
                "Un administrador no puede tener un departamento asignado",
                status_code=400,
                code="admin_department_not_allowed",
            )
        update_data["department_id"] = None
        return update_data

    if update_data.get("department_id", user.department_id) is None:
        raise AppError(
            "Un empleado debe tener un departamento asignado",
            status_code=400,
            code="department_required",
        )
    return update_data


def _ensure_email_is_available(
    db: Session, email: str, *, exclude_id: int
) -> None:
    statement = select(User.id).where(
        User.email == email,
        User.id != exclude_id,
    )
    if db.scalar(statement) is not None:
        raise ConflictError("Ya existe un usuario con ese correo electrónico")


def _ensure_department_exists(db: Session, department_id: int) -> None:
    department = db.get(Department, department_id)
    if department is None:
        raise NotFoundError("El departamento no existe")
