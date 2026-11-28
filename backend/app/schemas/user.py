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
            raise ValueError("La nueva contraseña y la confirmación no coinciden")
        if self.new_password == self.current_password:
            raise ValueError("La nueva contraseña debe ser distinta de la actual")
        return self


class UserCreate(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=120,
        description="Nombre completo del empleado",
    )
    email: str = Field(
        min_length=3,
        max_length=150,
        description="Correo electrónico único",
    )
    temporary_password: str = Field(
        min_length=10,
        max_length=128,
        description="Contraseña temporal que el empleado debe cambiar en el primer inicio de sesión",
    )
    department_id: int = Field(
        description="Id del departamento (grupo) asignado",
    )

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized or len(normalized) < 3:
            raise ValueError("El correo debe tener al menos 3 caracteres")
        if not EMAIL_PATTERN.match(normalized):
            raise ValueError("Formato de correo no válido")
        return normalized


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(
        default=None, min_length=1, max_length=120, description="Nombre completo del empleado"
    )
    email: str | None = Field(
        default=None, min_length=3, max_length=150, description="Correo electrónico único"
    )
    department_id: int | None = Field(
        default=None, description="Id del departamento (obligatorio si el rol es EMPLOYEE)"
    )
    role: str | None = Field(
        default=None,
        pattern="^(ADMIN|EMPLOYEE)$",
        description="Rol del empleado: ADMIN o EMPLOYEE",
    )

    @field_validator("email", mode="after")
    @classmethod
    def _normalize_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if not normalized or len(normalized) < 3:
            raise ValueError("El correo debe tener al menos 3 caracteres")
        return normalized
