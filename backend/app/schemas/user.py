from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Payload for registering a new employee (PEB-15 / HU-07)."""

    email: EmailStr = Field(
        ...,
        description="Unique employee corporate email address",
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=120,
        description="Full legal name of the employee",
    )
    temporary_password: str = Field(
        ...,
        min_length=8,
        description="Initial temporary password assigned by HR (minimum 8 characters)",
    )
    department_id: int = Field(
        ...,
        description="Mandatory foreign key referencing the assigned department (departments.id)",
    )


class UserResponse(BaseModel):
    """Public employee profile response exposing safe fields without sensitive hashes."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: str
    department_id: int
    is_active: bool
    must_change_password: bool
    created_at: datetime