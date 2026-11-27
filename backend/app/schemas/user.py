from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator, model_validator

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=10, max_length=128)
    confirm_password: str = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def _validate(self) -> "ChangePasswordRequest":
        if self.new_password != self.confirm_password:
            raise ValueError("New password and confirmation do not match")
        if self.new_password == self.current_password:
            raise ValueError("New password must be different from current password")
        return self


class UserCreate(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=120,
        description="Employee full name",
    )
    email: str = Field(
        min_length=3,
        max_length=150,
        description="Unique email address",
    )
    temporary_password: str = Field(
        min_length=10,
        max_length=128,
        description="Temporary password employee must change on first login",
    )
    department_id: int = Field(
        description="Assigned department (group) ID",
    )

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized or len(normalized) < 3:
            raise ValueError("Email must have at least 3 characters")
        if not EMAIL_PATTERN.match(normalized):
            raise ValueError("Invalid email format")
        return normalized


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(
        default=None, min_length=1, max_length=120, description="Employee full name"
    )
    email: str | None = Field(
        default=None, min_length=3, max_length=150, description="Unique email address"
    )
    department_id: int | None = Field(
        default=None, description="Department ID (required if role is EMPLOYEE)"
    )
    role: str | None = Field(
        default=None,
        pattern="^(ADMIN|EMPLOYEE)$",
        description="Employee role: ADMIN or EMPLOYEE",
    )

    @field_validator("email", mode="after")
    @classmethod
    def _normalize_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if not normalized or len(normalized) < 3:
            raise ValueError("Email must have at least 3 characters")
        return normalized
