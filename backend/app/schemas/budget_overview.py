from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field

from app.schemas.budget_common import Money
from app.schemas.budget_department import DepartmentBudgetResponse


class MonthlyBudgetOverview(BaseModel):
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