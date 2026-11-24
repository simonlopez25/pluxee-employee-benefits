"""Schemas para el presupuesto departamental mensual."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.budget_common import first_day, validate_non_negative


class DepartmentBudgetUpsert(BaseModel):
    """Payload de PUT /api/budgets/departments/{department_id}."""

    period: date = Field(description="Mes del presupuesto (cualquier día del mes se normaliza al día 1)")
    allocated_amount: Decimal = Field(
        ge=0, description="Importe asignado al departamento en ese mes (>= 0)"
    )

    @field_validator("period", mode="after")
    @classmethod
    def period_must_be_first_day(cls, value: date) -> date:
        """Normaliza el periodo al día 1 del mes."""
        return first_day(value)

    @field_validator("allocated_amount", mode="after")
    @classmethod
    def allocated_amount_must_be_non_negative(cls, value: Decimal) -> Decimal:
        return validate_non_negative(value, "importe asignado")


class DepartmentBudgetResponse(BaseModel):
    """Respuesta del presupuesto de un departamento en un mes."""

    id: int = Field(description="Identificador del presupuesto departamental")
    department_id: int = Field(description="Identificador del departamento")
    department_name: str = Field(description="Nombre del departamento")
    period: date = Field(description="Mes del presupuesto (día 1)")
    allocated_amount: Decimal = Field(description="Importe asignado al departamento")
    consumed_amount: Decimal = Field(
        description="Importe consumido (gastos aprobados del mes); 0 si no hay datos"
    )
    available_amount: Decimal = Field(
        description="Saldo disponible del departamento (asignado menos consumido)"
    )
    usage_percentage: float = Field(description="Porcentaje de uso del presupuesto asignado")
    benefit_references: list = Field(
        default_factory=list,
        description="Referencias informativas y orientativas por beneficio",
    )