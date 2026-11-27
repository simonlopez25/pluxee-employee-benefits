from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.schemas.budget import (
    BenefitReferenceItemIn,
    DepartmentBudgetResponse,
    GlobalBudgetResponse,
    MonthlyBudgetOverview,
)

from app.services.budget_allocation import (
    get_department_budget,
    get_global_budget_response,
    upsert_department_budget,
    upsert_global_budget,
    upsert_benefit_references,
)
from app.services.budget_overview import get_monthly_budget_overview
from app.services.budget_queries import (
    _department_budget_detail,
    _global_budget_response,
    first_day,
)

__all__ = [
    "first_day",
    "upsert_global_budget",
    "get_global_budget_response",
    "_global_budget_response",
    "upsert_department_budget",
    "_department_budget_detail",
    "get_department_budget",
    "upsert_benefit_references",
    "get_monthly_budget_overview",
]