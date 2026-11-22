"""Esquemas de departamentos."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DepartmentResponse(BaseModel):
    """Respuesta de GET /api/departments."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {"id": 1, "name": "Ventas", "is_active": True}
        },
    )

    id: int = Field(description="Identificador único del departamento")
    name: str = Field(description="Nombre del departamento")
    is_active: bool = Field(description="Departamento activo")
