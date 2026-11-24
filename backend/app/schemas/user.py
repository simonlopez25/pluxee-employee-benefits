from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, model_validator


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=10, max_length=128)
    confirm_password: str = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def _validate(self) -> "ChangePasswordRequest":
        if self.new_password != self.confirm_password:
            raise ValueError("La nueva contraseña y su confirmación no coinciden")
        if self.new_password == self.current_password:
            raise ValueError("La nueva contraseña debe ser diferente a la actual")
        return self


class UserUpdateRequest(BaseModel):
    """Payload de PATCH /api/users/{user_id}: edición parcial de empleado.

    Todos los campos son opcionales; solo se modifican los enviados.
    """

    full_name: str | None = Field(
        default=None, min_length=1, max_length=120, description="Nombre completo del empleado"
    )
    email: str | None = Field(
        default=None, min_length=3, max_length=150, description="Correo electrónico único"
    )
    department_id: int | None = Field(
        default=None, description="Id del departamento (requerido si rol es EMPLOYEE)"
    )
    role: str | None = Field(
        default=None,
        pattern="^(ADMIN|EMPLOYEE)$",
        description="Rol del empleado: ADMIN o EMPLOYEE",
    )

    @field_validator("email", mode="after")
    @classmethod
    def _normalize_email(cls, value: str | None) -> str | None:
        """Normaliza el email (trim + minúsculas) antes de guardarlo.

        El frontend ya lo envía normalizado; aquí se garantiza también para
        llamadas directas a la API, de modo que la unicidad no dependa de la
        colación y el login (que normaliza igual) siempre encuentre al usuario.
        """
        if value is None:
            return None
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("El correo electrónico no puede estar vacío")
        return normalized
