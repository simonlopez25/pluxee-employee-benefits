from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppError, ConflictError, NotFoundError
from app.core.security import hash_password, verify_password
from app.models.department import Department
from app.models.user import User
from app.schemas.auth import UserPublic
from app.schemas.user import ChangePasswordRequest, UserCreate, UserUpdateRequest


def change_password(
    db: Session, user: User, data: ChangePasswordRequest
) -> UserPublic:
    if not verify_password(data.current_password, user.password_hash):
        raise AppError(
            "Current password is incorrect",
            status_code=400,
            code="invalid_current_password",
        )

    user.password_hash = hash_password(data.new_password)
    user.must_change_password = False
    db.commit()
    db.refresh(user)
    return UserPublic.model_validate(user)


def create_employee(db: Session, payload: UserCreate) -> UserPublic:
    if (
        db.scalar(select(User.id).where(User.email == payload.email)) is not None
    ):
        raise ConflictError("A user with that email already exists")

    department = db.get(Department, payload.department_id)
    if department is None or not department.is_active:
        raise NotFoundError("Department does not exist or is inactive")

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
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(
            "A user with that email already exists"
        ) from exc
    db.refresh(user)
    return UserPublic.model_validate(user)


def update_employee(
    db: Session,
    user_id: int,
    current_user: User,
    payload: UserUpdateRequest,
) -> UserPublic:
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
    user = _get_user_or_404(db, user_id)

    if current_user.id == user_id:
        raise AppError(
            "You cannot deactivate yourself",
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


def list_users(db: Session) -> list[UserPublic]:
    statement = select(User).order_by(User.id)
    users = list(db.scalars(statement).all())
    return [UserPublic.model_validate(user) for user in users]


def _get_user_or_404(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError("Employee does not exist")
    return user


def _validate_role_change(
    current_user: User, user_id: int, new_role: str
) -> None:
    if current_user.id == user_id and new_role != "ADMIN":
        raise AppError(
            "An admin cannot downgrade their own role",
            status_code=400,
            code="self_role_downgrade",
        )


def _validate_and_normalize_role_department(
    update_data: dict, user: User
) -> dict:
    final_role = update_data.get("role", user.role)

    if final_role == "ADMIN":
        if "department_id" in update_data and update_data["department_id"] is not None:
            raise AppError(
                "An admin cannot have a department assigned",
                status_code=400,
                code="admin_department_not_allowed",
            )
        update_data["department_id"] = None
        return update_data

    if update_data.get("department_id", user.department_id) is None:
        raise AppError(
            "An employee must have a department assigned",
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
        raise ConflictError("A user with that email already exists")


def _ensure_department_exists(db: Session, department_id: int) -> None:
    department = db.get(Department, department_id)
    if department is None:
        raise NotFoundError("Department does not exist")
