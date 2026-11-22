"""Lógica de negocio de presupuestos (HU-11 / PEB-19).

Meses independientes sin arrastre de saldo: el global no baja de lo ya
repartido (suelo) y la suma departamental no lo supera (techo).
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
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
    BenefitReferenceItemIn,
    DepartmentBudgetResponse,
    GlobalBudgetResponse,
    MonthlyBudgetOverview,
)

ZERO = Decimal("0")


def first_day(period: date) -> date:
    """Normaliza cualquier fecha de un mes al día 1 de ese mes."""
    return period.replace(day=1)


def _month_range(period: date) -> tuple[date, date]:
    """Devuelve (primer día, primer día del mes siguiente) de la fecha dada."""
    start = period.replace(day=1)
    if start.month == 12:
        end = date(start.year + 1, 1, 1)
    else:
        end = date(start.year, start.month + 1, 1)
    return start, end


def upsert_global_budget(
    db: Session, period: date, total_amount: Decimal
) -> GlobalBudget:
    """Crea o actualiza el global; 409 si bajaría de lo ya repartido (suelo)."""
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


def upsert_department_budget(
    db: Session,
    department_id: int,
    period: date,
    allocated_amount: Decimal,
) -> DepartmentBudget:
    """Crea o actualiza el presupuesto de un departamento; valida activo, global y techo."""
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


def _consumed_amount(db: Session, department_id: int, period: date) -> Decimal:
    """Suma de gastos aprobados del mes de los empleados del departamento."""
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


def upsert_benefit_references(
    db: Session,
    department_id: int,
    period: date,
    references: list[BenefitReferenceItemIn],
) -> DepartmentBudgetResponse:
    """Guarda las referencias orientativas por beneficio, sin topes."""
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

    # Pydantic ya valida ge=0; aquí se refuerza a nivel de servicio.
    for ref in references:
        if ref.indicative_amount < 0:
            raise ConflictError(
                f"indicative_amount for benefit {ref.benefit_id} cannot be negative"
            )

    # Reemplaza todas las referencias del mes (upsert por lote).
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


def get_monthly_budget_overview(db: Session, period: date) -> MonthlyBudgetOverview:
    """Resumen del mes; sin global devuelve ceros en vez de error 500."""
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

    # Presupuestos departamentales del mes, ordenados por nombre.
    department_budgets = db.execute(
        select(DepartmentBudget)
        .join(Department, Department.id == DepartmentBudget.department_id)
        .where(DepartmentBudget.global_budget_id == global_budget.id)
        .order_by(Department.name)
    ).scalars().all()

    allocated_total = sum((db.amount for db in department_budgets), ZERO)

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
