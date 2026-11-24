"""Lógica de negocio del saldo del empleado (HU-13 / PEB-55).

Restante = Asignado − Aprobado − Pendiente (los PENDING descuentan saldo).
El saldo es mensual: solo cuentan las asignaciones activas cuyo paquete
pertenece a un departamento con presupuesto en el mes en curso. Si el mes
no está abierto todavía, se devuelven las asignaciones activas con su
saldo íntegro (approved = pending = 0) para no romper la vista.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.benefit import Benefit
from app.models.department_budget import DepartmentBudget
from app.models.employee_assignment import EmployeeAssignment
from app.models.expense import Expense
from app.models.expense_allocation import ExpenseAllocation
from app.models.global_budget import GlobalBudget
from app.models.package import Package
from app.models.package_benefit import PackageBenefit
from app.schemas.balance import (
    BenefitBalance,
    EmployeeBalanceResponse,
    PackageBalance,
)

_ZERO = Decimal("0.00")


def _current_period(db: Session) -> date | None:
    """Devuelve el `period` del presupuesto global del mes en curso, si existe."""
    today = date.today()
    period = date(today.year, today.month, 1)
    exists = db.scalar(
        select(GlobalBudget.period).where(GlobalBudget.period == period)
    )
    return exists


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"))


def get_balance(db: Session, user_id: int) -> EmployeeBalanceResponse:
    """Calcula el saldo del empleado por beneficio y por paquete."""
    period = _current_period(db)

    # Paquetes visibles: asignaciones activas del empleado. Si hay presupuesto
    # del mes, se restringe a los paquetes del departamento con presupuesto
    # en ese mes; si no, se muestran todas las asignaciones activas.
    assignment_stmt = (
        select(EmployeeAssignment)
        .where(
            EmployeeAssignment.user_id == user_id,
            EmployeeAssignment.is_active.is_(True),
        )
    )
    assignments = list(db.scalars(assignment_stmt))

    if period is not None and assignments:
        visible_package_ids = set(
            db.scalars(
                select(Package.id)
                .join(
                    DepartmentBudget,
                    DepartmentBudget.department_id == Package.department_id,
                )
                .join(
                    GlobalBudget,
                    GlobalBudget.id == DepartmentBudget.global_budget_id,
                )
                .where(
                    GlobalBudget.period == period,
                    Package.id.in_([a.package_id for a in assignments]),
                )
            )
        )
        assignments = [a for a in assignments if a.package_id in visible_package_ids]

    if not assignments:
        return EmployeeBalanceResponse(
            period=period,
            assigned_total=_ZERO,
            approved_total=_ZERO,
            pending_total=_ZERO,
            consumed_total=_ZERO,
            available_total=_ZERO,
            by_benefit=[],
            packages=[],
        )

    package_ids = [a.package_id for a in assignments]
    assignment_ids = [a.id for a in assignments]

    # Beneficios que cubre cada paquete (package_benefits).
    package_benefit_rows = db.execute(
        select(PackageBenefit.package_id, Benefit)
        .join(Benefit, Benefit.id == PackageBenefit.benefit_id)
        .where(PackageBenefit.package_id.in_(package_ids))
    ).all()

    benefits_by_package: dict[int, list[Benefit]] = defaultdict(list)
    for package_id, benefit in package_benefit_rows:
        benefits_by_package[package_id].append(benefit)

    # Consumo por (asignación, beneficio): suma de allocations no rechazadas.
    allocation_rows = db.execute(
        select(
            ExpenseAllocation.employee_assignment_id,
            ExpenseAllocation.benefit_id,
            Expense.status,
            ExpenseAllocation.amount,
        )
        .join(Expense, Expense.id == ExpenseAllocation.expense_id)
        .where(
            ExpenseAllocation.employee_assignment_id.in_(assignment_ids),
            Expense.status.in_(("APPROVED", "PENDING")),
        )
    ).all()

    approved_by: dict[tuple[int, int], Decimal] = defaultdict(lambda: _ZERO)
    pending_by: dict[tuple[int, int], Decimal] = defaultdict(lambda: _ZERO)
    for assignment_id, benefit_id, status, amount in allocation_rows:
        key = (assignment_id, benefit_id)
        if status == "APPROVED":
            approved_by[key] += amount
        else:
            pending_by[key] += amount

    packages_by_id = {
        p.id: p for p in db.scalars(select(Package).where(Package.id.in_(package_ids)))
    }

    # Construcción de la respuesta
    package_results: list[PackageBalance] = []
    aggregate: dict[int, BenefitBalance] = {}

    for assignment in assignments:
        package = packages_by_id.get(assignment.package_id)
        if package is None:
            continue

        package_benefits: list[BenefitBalance] = []
        package_approved = _ZERO
        package_pending = _ZERO
        package_assigned = assignment.assigned_amount

        for benefit in benefits_by_package.get(package.id, []):
            key = (assignment.id, benefit.id)
            approved = _quantize(approved_by.get(key, _ZERO))
            pending = _quantize(pending_by.get(key, _ZERO))
            consumed = _quantize(approved + pending)
            # El reparto del importe del paquete entre sus beneficios no está
            # definido por el esquema; cada beneficio hereda el importe del
            # paquete para el cálculo del disponible individual. El total del
            # paquete es la fuente de verdad y se calcula con el asignado real.
            benefit_available = _quantize(package_assigned - consumed)

            item = BenefitBalance(
                benefit_id=benefit.id,
                benefit_name=benefit.name,
                is_basic=benefit.is_basic,
                assigned=_quantize(package_assigned),
                approved=approved,
                pending=pending,
                consumed=consumed,
                available=benefit_available,
            )
            package_benefits.append(item)

            package_approved += approved
            package_pending += pending

            # Agregado por beneficio a nivel global del empleado
            if benefit.id in aggregate:
                agg = aggregate[benefit.id]
                agg.assigned = _quantize(agg.assigned + package_assigned)
                agg.approved = _quantize(agg.approved + approved)
                agg.pending = _quantize(agg.pending + pending)
                agg.consumed = _quantize(agg.consumed + consumed)
                agg.available = _quantize(agg.available + benefit_available)
            else:
                aggregate[benefit.id] = BenefitBalance(
                    benefit_id=benefit.id,
                    benefit_name=benefit.name,
                    is_basic=benefit.is_basic,
                    assigned=_quantize(package_assigned),
                    approved=approved,
                    pending=pending,
                    consumed=consumed,
                    available=benefit_available,
                )

        package_results.append(
            PackageBalance(
                package_id=package.id,
                package_name=package.name,
                assigned=_quantize(package_assigned),
                approved=_quantize(package_approved),
                pending=_quantize(package_pending),
                consumed=_quantize(package_approved + package_pending),
                available=_quantize(
                    package_assigned - package_approved - package_pending
                ),
                benefits=package_benefits,
            )
        )

    by_benefit = sorted(aggregate.values(), key=lambda b: b.benefit_name)
    package_results.sort(key=lambda p: p.package_name)

    assigned_total = _quantize(sum((p.assigned for p in package_results), _ZERO))
    approved_total = _quantize(sum((p.approved for p in package_results), _ZERO))
    pending_total = _quantize(sum((p.pending for p in package_results), _ZERO))
    consumed_total = _quantize(approved_total + pending_total)
    available_total = _quantize(assigned_total - consumed_total)

    return EmployeeBalanceResponse(
        period=period,
        assigned_total=assigned_total,
        approved_total=approved_total,
        pending_total=pending_total,
        consumed_total=consumed_total,
        available_total=available_total,
        by_benefit=by_benefit,
        packages=package_results,
    )