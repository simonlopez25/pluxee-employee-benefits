"""Esquemas de departamentos."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

DepartmentName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]
CurrencyCode = Annotated[
    str, StringConstraints(pattern=r"^[A-Za-z]{3}$", to_upper=True)
]


class DepartmentBase(BaseModel):
    """Campos que comparten crear y editar."""

    name: DepartmentName = Field(description="Nombre del departamento")
    currency: CurrencyCode = Field(description="Divisa de 3 letras, por ejemplo EUR")


class DepartmentCreate(DepartmentBase):
    """Cuerpo de POST /api/departments."""


class DepartmentUpdate(DepartmentBase):
    """Cuerpo de PUT /api/departments/{id}."""


class DepartmentResponse(DepartmentBase):
    """Departamento tal como lo devuelve la API."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Ventas",
                "currency": "EUR",
                "is_active": True,
                "created_at": "2026-11-20T09:45:49Z",
            }
        },
    )

    id: int = Field(description="Identificador único del departamento")
    is_active: bool = Field(description="Departamento activo")
    created_at: datetime = Field(description="Fecha de creación")


# --- Añadido para la lista de departamentos ---


class DepartmentPackageSummary(BaseModel):
    """Resumen de un paquete activo asociado al departamento."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Identificador único del paquete")
    name: str = Field(description="Nombre del paquete")


class DepartmentListResponse(DepartmentResponse):
    """Elemento de la lista de departamentos con métricas y paquetes activos."""

    employee_count: int = Field(
        default=0,
        description="Número de empleados activos asignados al departamento",
    )
    packages: list[DepartmentPackageSummary] = Field(
        default_factory=list,
        description="Paquetes activos asociados al departamento",
    )