from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import AppError
from app.core.security import hash_password
from app.models.department import Department
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new employee (HU-07 / PEB-15)",
)
def register_employee(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> User:
    """
    Register a new employee account meeting all HU-07 acceptance criteria:
    1. Mandatory assignment to a single valid, active department (department_id).
    2. Email uniqueness check across the entire users table.
    3. Mandatory password change flag enabled on creation (must_change_password = True).
    4. Secure password storage using salted bcrypt hashing (never returned in plain text).
    """
    # 1. Normalize email address and verify uniqueness
    normalized_email = user_in.email.strip().lower()
    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user:
        raise AppError(
            code="USER_EMAIL_ALREADY_EXISTS",
            message="An account with this email address already exists.",
            status_code=status.HTTP_409_CONFLICT,
        )

    # 2. Verify that the specified department exists and is currently active
    department = (
        db.query(Department)
        .filter(
            Department.id == user_in.department_id,
            Department.is_active == True,
        )
        .first()
    )
    if not department:
        raise AppError(
            code="DEPARTMENT_NOT_FOUND",
            message="The specified department does not exist or is inactive.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # 3. Instantiate employee record with role partition and security defaults
    new_user = User(
        email=normalized_email,
        full_name=user_in.full_name.strip(),
        password_hash=hash_password(user_in.temporary_password),
        department_id=user_in.department_id,
        role="EMPLOYEE",
        is_active=True,
        must_change_password=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user