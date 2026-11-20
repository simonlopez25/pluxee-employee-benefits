"""Schemas de los endpoints de departamentos."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

DepartmentName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]
CurrencyCode = Annotated[
    str, StringConstraints(pattern=r"^[A-Za-z]{3}$", to_upper=True)
]


class DepartmentBase(BaseModel):
    """Campos que comparten crear y editar."""

    name: DepartmentName
    currency: CurrencyCode


class DepartmentCreate(DepartmentBase):
    """Cuerpo de POST /api/departments."""


class DepartmentUpdate(DepartmentBase):
    """Cuerpo de PUT /api/departments/{id}."""


class DepartmentResponse(DepartmentBase):
    """Departamento tal como lo devuelve la API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime