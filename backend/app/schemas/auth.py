from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=1, max_length=128)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    role: str
    department_id: int | None
    must_change_password: bool
    is_active: bool = Field(description="Cuenta activa (puede acceder a la plataforma)")
    deactivated_at: datetime | None = Field(
        description="Fecha y hora de baja lógica (UTC), null si está activo"
    )


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserPublic