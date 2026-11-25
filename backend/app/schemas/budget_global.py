"""Schemas para el presupuesto global mensual."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.budget_common import Money, first_day, validate_non_negative


class GlobalBudgetBase(BaseModel):
    """Campos compartidos del presupuesto mensual global."""

    period: date = Field(description="Mes del presupuesto (cualquier día del mes se normaliza al día 1)")
    total_amount: Money = Field(
        ge=0, description="Importe total del presupuesto mensual global (>= 0)"
    )

    @field_validator("period", mode="after")
    @classmethod
    def period_must_be_first_day(cls, value: date) -> date:
        """Normaliza el periodo al día 1 del mes."""
        return first_day(value)

    @field_validator("total_amount", mode="after")
    @classmethod
    def total_amount_must_be_non_negative(cls, value: Decimal) -> Decimal:
        return validate_non_negative(value, "importe total")


class GlobalBudgetUpsert(GlobalBudgetBase):
    """Payload de PUT /api/budgets/global."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "period": "2026-11-15",
                "total_amount": "10000.00",
            }
        }
    )


class GlobalBudgetResponse(BaseModel):
    """Respuesta de presupuesto mensual global con campos calculados."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Identificador único del presupuesto global")
    period: date = Field(description="Mes del presupuesto (día 1)")
    total_amount: Money = Field(description="Importe total del presupuesto global")
    allocated_to_departments: Money = Field(
        description="Importe ya repartido entre los departamentos del mes"
    )
    unallocated_amount: Money = Field(
        description="Importe del global aún sin repartir"
    )
    created_at: datetime = Field(description="Fecha de creación")
    updated_at: datetime = Field(description="Última actualización")