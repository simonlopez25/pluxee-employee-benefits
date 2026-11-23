"""Pydantic schemas del módulo de presupuestos (presupuestos en 2 niveles
y referencias informativas por beneficio)."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, field_validator

# Siempre 2 decimales en las respuestas monetarias (coherente con NUMERIC(12,2)).
Money = Annotated[
    Decimal,
    PlainSerializer(lambda v: f"{v:.2f}", return_type=str),
]


def _first_day(value: date) -> date:
    """Devuelve el día 1 del mes de la fecha recibida."""
    return value.replace(day=1)


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
        return _first_day(value)

    @field_validator("total_amount", mode="after")
    @classmethod
    def total_amount_must_be_non_negative(cls, value: Decimal) -> Decimal:
        if value < 0:
            raise ValueError("El importe total no puede ser negativo")
        return value


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
        return _first_day(value)

    @field_validator("allocated_amount", mode="after")
    @classmethod
    def allocated_amount_must_be_non_negative(cls, value: Decimal) -> Decimal:
        if value < 0:
            raise ValueError("El importe asignado no puede ser negativo")
        return value


class BenefitReferenceItem(BaseModel):
    """Importe orientativo de un beneficio dentro de un presupuesto departamental."""

    benefit_id: int = Field(description="Identificador del beneficio")
    benefit_name: str = Field(description="Nombre del beneficio")
    indicative_amount: Money = Field(description="Importe orientativo (>= 0)")


class BenefitReferenceItemIn(BaseModel):
    """Entrada de una referencia orientativa por beneficio."""

    benefit_id: int = Field(description="Identificador del beneficio")
    indicative_amount: Decimal = Field(
        ge=0, description="Importe orientativo del beneficio (>= 0)"
    )


class BenefitReferenceBulkUpdate(BaseModel):
    """Payload de PUT /api/budgets/departments/{department_id}/references."""

    period: date = Field(description="Mes de las referencias (se normaliza al día 1)")
    references: list[BenefitReferenceItemIn] = Field(
        default_factory=list,
        description="Referencias orientativas por beneficio del departamento en ese mes",
    )

    @field_validator("period", mode="after")
    @classmethod
    def period_must_be_first_day(cls, value: date) -> date:
        """Normaliza el periodo al día 1 del mes."""
        return _first_day(value)


class DepartmentBudgetResponse(BaseModel):
    """Respuesta del presupuesto de un departamento en un mes."""

    id: int = Field(description="Identificador del presupuesto departamental")
    department_id: int = Field(description="Identificador del departamento")
    department_name: str = Field(description="Nombre del departamento")
    period: date = Field(description="Mes del presupuesto (día 1)")
    allocated_amount: Money = Field(description="Importe asignado al departamento")
    consumed_amount: Money = Field(
        description="Importe consumido (gastos aprobados del mes); 0 si no hay datos"
    )
    available_amount: Money = Field(
        description="Saldo disponible del departamento (asignado menos consumido)"
    )
    usage_percentage: float = Field(description="Porcentaje de uso del presupuesto asignado")
    benefit_references: list[BenefitReferenceItem] = Field(
        default_factory=list,
        description="Referencias informativas y orientativas por beneficio",
    )


class MonthlyBudgetOverview(BaseModel):
    """Resumen completo de presupuestos de un mes."""

    period: date = Field(description="Mes consultado (día 1)")
    total_amount: Money = Field(description="Presupuesto global del mes (0 si no está configurado)")
    allocated_to_departments: Money = Field(
        description="Suma de los presupuestos departamentales del mes"
    )
    unallocated_amount: Money = Field(
        description="Saldo del global aún sin repartir entre departamentos"
    )
    departments: list[DepartmentBudgetResponse] = Field(
        default_factory=list,
        description="Presupuesto de cada departamento con sus referencias orientativas",
    )
