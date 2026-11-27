from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models import Department, DepartmentBudget, GlobalBudget
from app.schemas.budget import DepartmentBudgetResponse, GlobalBudgetResponse
from app.services.budget_queries import (
    _department_budget_detail,
    _global_budget_response,
    first_day,
)

ZERO = Decimal("0")


def upsert_global_budget(
    db: Session, period: date, total_amount: Decimal
) -> GlobalBudget:
    period = first_day(period)
    row = db.scalar(select(GlobalBudget).where(GlobalBudget.period == period))
    if row is None:
        row = GlobalBudget(
            period=period,
            amount=total_amount,
            updated_at=datetime.now(timezone.utc),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    allocated = db.scalar(
        select(func.coalesce(func.sum(DepartmentBudget.amount), 0)).where(
            DepartmentBudget.global_budget_id == row.id
        )
    )
    allocated = allocated or ZERO
    if total_amount < allocated:
        raise ConflictError(
            f"No se puede reducir el presupuesto global a {total_amount}: "
            f"ya se repartieron {allocated} entre los departamentos de {period}. "
            f"Importe mínimo válido: {allocated}."
        )
    row.amount = total_amount
    row.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return row


def get_global_budget_response(db: Session, period: date) -> GlobalBudgetResponse | None:
    period = first_day(period)
    row = db.scalar(select(GlobalBudget).where(GlobalBudget.period == period))
    if row is None:
        return None
    return _global_budget_response(db, row)


def upsert_department_budget(
    db: Session,
    department_id: int,
    period: date,
    allocated_amount: Decimal,
) -> DepartmentBudget:
    period = first_day(period)

    department = db.get(Department, department_id)
    if department is None:
        raise NotFoundError(f"Department {department_id} not found")
    if not department.is_active:
        raise ConflictError(f"Department {department_id} ({department.name}) is not active")

    global_budget = db.scalar(select(GlobalBudget).where(GlobalBudget.period == period))
    if global_budget is None:
        raise ConflictError(
            f"No global budget for period {period} (create it first before assigning department budgets)"
        )

    allocated_by_others = db.scalar(
        select(func.coalesce(func.sum(DepartmentBudget.amount), 0)).where(
            DepartmentBudget.global_budget_id == global_budget.id,
            DepartmentBudget.department_id != department_id,
        )
    )
    allocated_by_others = allocated_by_others or ZERO

    new_total = allocated_by_others + allocated_amount
    if new_total > global_budget.amount:
        available = global_budget.amount - allocated_by_others
        raise ConflictError(
            f"Department budget of {allocated_amount} would exceed the global budget "
            f"({global_budget.amount}) for {period}. "
            f"Amount available to distribute: {available}."
        )

    existing = db.scalar(
        select(DepartmentBudget).where(
            DepartmentBudget.global_budget_id == global_budget.id,
            DepartmentBudget.department_id == department_id,
        )
    )
    if existing is None:
        row = DepartmentBudget(
            global_budget_id=global_budget.id,
            department_id=department_id,
            amount=allocated_amount,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
    else:
        existing.amount = allocated_amount
        db.commit()
        db.refresh(existing)
        row = existing
    return row


def get_department_budget(db: Session, department_id: int, period: date):
    period = first_day(period)
    global_budget = db.scalar(select(GlobalBudget).where(GlobalBudget.period == period))
    if global_budget is None:
        return None
    return db.scalar(
        select(DepartmentBudget).where(
            DepartmentBudget.global_budget_id == global_budget.id,
            DepartmentBudget.department_id == department_id,
        )
    )


def upsert_benefit_references(
    db: Session,
    department_id: int,
    period: date,
    references: list,
) -> DepartmentBudgetResponse:
    from app.models import Benefit, BenefitBudgetReference
    from app.schemas.budget import BenefitReferenceItemIn

    period = first_day(period)

    department = db.get(Department, department_id)
    if department is None:
        raise NotFoundError(f"Department {department_id} not found")

    global_budget = db.scalar(select(GlobalBudget).where(GlobalBudget.period == period))
    if global_budget is None:
        raise ConflictError(
            f"No global budget for period {period} (create it first before adding benefit references)"
        )

    department_budget = db.scalar(
        select(DepartmentBudget).where(
            DepartmentBudget.global_budget_id == global_budget.id,
            DepartmentBudget.department_id == department_id,
        )
    )
    if department_budget is None:
        raise ConflictError(
            f"No department budget for department {department_id} in period {period} "
            f"(create it first before adding benefit references)"
        )

    for ref in references:
        if ref.indicative_amount < 0:
            raise ConflictError(
                f"indicative_amount for benefit {ref.benefit_id} cannot be negative"
            )

    db.execute(
        delete(BenefitBudgetReference).where(
            BenefitBudgetReference.department_budget_id == department_budget.id
        )
    )
    rows = []
    for ref in references:
        benefit = db.get(Benefit, ref.benefit_id)
        if benefit is None:
            raise NotFoundError(f"Benefit {ref.benefit_id} not found")
        row = BenefitBudgetReference(
            department_budget_id=department_budget.id,
            benefit_id=ref.benefit_id,
            indicative_amount=ref.indicative_amount,
        )
        db.add(row)
        rows.append(row)
    db.commit()
    for row in rows:
        db.refresh(row)
    return _department_budget_detail(db, department_budget)