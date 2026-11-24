"""Pydantic schemas del módulo de presupuestos (presupuestos en 2 niveles
y referencias informativas por beneficio).

Re-exporta todos los schemas desde módulos especializados:
- budget_common: tipos y validadores compartidos
- budget_global: schemas de presupuesto global
- budget_department: schemas de presupuesto departamental
- budget_benefit: schemas de referencias por beneficio
- budget_overview: schema de vista general mensual
"""

from __future__ import annotations

from app.schemas.budget_benefit import (
    BenefitReferenceBulkUpdate,
    BenefitReferenceItem,
    BenefitReferenceItemIn,
)
from app.schemas.budget_department import (
    DepartmentBudgetResponse,
    DepartmentBudgetUpsert,
)
from app.schemas.budget_global import (
    GlobalBudgetBase,
    GlobalBudgetResponse,
    GlobalBudgetUpsert,
)
from app.schemas.budget_overview import MonthlyBudgetOverview

__all__ = [
    # Global
    "GlobalBudgetBase",
    "GlobalBudgetUpsert",
    "GlobalBudgetResponse",
    # Department
    "DepartmentBudgetUpsert",
    "DepartmentBudgetResponse",
    # Benefit references
    "BenefitReferenceItem",
    "BenefitReferenceItemIn",
    "BenefitReferenceBulkUpdate",
    # Overview
    "MonthlyBudgetOverview",
]