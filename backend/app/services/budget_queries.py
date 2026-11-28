from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models import (
    Benefit,
    BenefitBudgetReference,
    Department,
    DepartmentBudget,
    EmployeeAssignment,
    Expense,
    ExpenseAllocation,
    GlobalBudget,
    User,
)
from app.schemas.budget import (
    BenefitReferenceItem,
    DepartmentBudgetResponse,
    GlobalBudgetResponse,
)

ZERO = Decimal("0")


def first_day(period: date) -> date:
    return period.replace(day=1)


def _month_range(period: date) -> tuple[date, date]:
    start = period.replace(day=1)
    if start.month == 12:
        end = date(start.year + 1, 1, 1)
    else:
        end = date(start.year, start.month + 1, 1)
    return start, end


def _consumed_amount(db: Session, department_id: int, period: date) -> Decimal:
    start, end = _month_range(period)
    return (
        db.scalar(
            select(func.coalesce(func.sum(ExpenseAllocation.amount), 0))
            .join(Expense, Expense.id == ExpenseAllocation.expense_id)
            .join(EmployeeAssignment, EmployeeAssignment.id == ExpenseAllocation.employee_assignment_id)
            .join(User, User.id == EmployeeAssignment.user_id)
            .where(Expense.status == "APPROVED")
            .where(Expense.expense_date >= start)
            .where(Expense.expense_date < end)
            .where(User.department_id == department_id)
        )
        or ZERO
    )


def _benefit_references(db: Session, department_budget_id: int) -> list[BenefitReferenceItem]:
    rows = db.execute(
        select(BenefitBudgetReference, Benefit)
        .join(Benefit, Benefit.id == BenefitBudgetReference.benefit_id)
        .where(BenefitBudgetReference.department_budget_id == department_budget_id)
        .order_by(Benefit.name)
    ).all()
    return [
        BenefitReferenceItem(
            benefit_id=row.BenefitBudgetReference.benefit_id,
            benefit_name=row.Benefit.name,
            indicative_amount=row.BenefitBudgetReference.indicative_amount,
        )
        for row in rows
    ]


def _global_budget_response(db: Session, row: GlobalBudget) -> GlobalBudgetResponse:
    allocated = db.scalar(
        select(func.coalesce(func.sum(DepartmentBudget.amount), 0)).where(
            DepartmentBudget.global_budget_id == row.id
        )
    )
    allocated = allocated or ZERO
    return GlobalBudgetResponse(
        id=row.id,
        period=row.period,
        total_amount=row.amount,
        allocated_to_departments=allocated,
        unallocated_amount=row.amount - allocated,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _department_budget_detail(
    db: Session, department_budget: DepartmentBudget
) -> DepartmentBudgetResponse:
    department = db.get(Department, department_budget.department_id)
    global_budget = db.get(GlobalBudget, department_budget.global_budget_id)
    period = global_budget.period
    consumed = _consumed_amount(db, department_budget.department_id, period)
    allocated = department_budget.amount
    available = allocated - consumed
    usage = (consumed / allocated * 100) if allocated > 0 else 0.0
    return DepartmentBudgetResponse(
        id=department_budget.id,
        department_id=department_budget.department_id,
        department_name=department.name if department else "",
        period=period,
        allocated_amount=allocated,
        consumed_amount=consumed,
        available_amount=available,
        usage_percentage=round(usage, 2),
        benefit_references=_benefit_references(db, department_budget.id),
    )