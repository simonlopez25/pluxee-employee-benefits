from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Department, DepartmentBudget, GlobalBudget
from app.schemas.budget import MonthlyBudgetOverview
from app.services.budget_allocation import get_global_budget_response
from app.services.budget_queries import (
    _department_budget_detail,
    first_day,
)

ZERO = Decimal("0")


def get_monthly_budget_overview(db: Session, period: date) -> MonthlyBudgetOverview:
    period = first_day(period)

    global_budget = db.scalar(select(GlobalBudget).where(GlobalBudget.period == period))
    if global_budget is None:
        return MonthlyBudgetOverview(
            period=period,
            total_amount=ZERO,
            allocated_to_departments=ZERO,
            unallocated_amount=ZERO,
            departments=[],
        )

    department_budgets = db.execute(
        select(DepartmentBudget)
        .join(Department, Department.id == DepartmentBudget.department_id)
        .where(DepartmentBudget.global_budget_id == global_budget.id)
        .order_by(Department.name)
    ).scalars().all()

    allocated_total = sum((d.amount for d in department_budgets), ZERO)

    departments_detail = [
        _department_budget_detail(db, db_row) for db_row in department_budgets
    ]

    return MonthlyBudgetOverview(
        period=global_budget.period,
        total_amount=global_budget.amount,
        allocated_to_departments=allocated_total,
        unallocated_amount=global_budget.amount - allocated_total,
        departments=departments_detail,
    )