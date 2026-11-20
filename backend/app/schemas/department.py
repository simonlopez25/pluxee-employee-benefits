"""Esquemas de Pydantic para el CRUD y gestión de departamentos."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class DepartmentCreate(BaseModel):
    """Esquema de entrada para crear un departamento existente."""

    name: str = Field(..., min_length=2, max_length=100, description="Nombre único del grupo o departamento")
    currency: str = Field("EUR", min_length=3, max_length=3, description="Código de divisa (ISO 4217, por defecto EUR)")


class DepartmentUpdate(BaseModel):
    """Esquema de entrada para editar un departamento existente."""

    name: str | None = Field(None, min_length=2, max_length=100, description="Nuevo nombre del departamento")
    currency: str | None = Field(None, min_length=3, max_length=3, description="Nueva divisa")
    is_active: bool | None = Field(None, description="Estado de activación del departamento")

class DepartmentDetailResponse(BaseModel):
    """Esquema de respuesta detallada para las tarjetas de la vista 02 Grupos."""

    id: int
    name: str
    currency: str
    is_active: bool
    created_at: datetime
    assigned_employees_count: int = Field(0, description="Número de empleados activos asignados al grupo")
    total_budget: Decimal = Field(Decimal("0.00"), description="Presupuesto asignado al departamento")
    package_count: int = Field(0, description="Número de paquetes asociados")

    model_config = ConfigDict(from_attributes=True)