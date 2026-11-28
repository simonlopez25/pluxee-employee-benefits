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
_CENT = Decimal("0.01")


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(_CENT)


def _current_period(db: Session) -> tuple[date, date] | None:
    today = date.today()
    first_day = date(today.year, today.month, 1)
    if today.month == 12:
        next_first_day = date(today.year + 1, 1, 1)
    else:
        next_first_day = date(today.year, today.month + 1, 1)

    exists = db.scalar(
        select(GlobalBudget.period).where(GlobalBudget.period == first_day)
    )
    if exists is None:
        return None
    return first_day, next_first_day


def _load_assignments(db: Session, user_id: int) -> list[EmployeeAssignment]:
    return list(
        db.scalars(
            select(EmployeeAssignment).where(
                EmployeeAssignment.user_id == user_id,
                EmployeeAssignment.is_active.is_(True),
            )
        )
    )


def _package_ids_with_department_budget(
    db: Session, assignments: list[EmployeeAssignment], first_day: date
) -> set[int]:
    if not assignments:
        return set()
    return set(
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
                GlobalBudget.period == first_day,
                Package.id.in_([a.package_id for a in assignments]),
            )
        )
    )


def _load_benefits_by_package(
    db: Session, package_ids: list[int]
) -> dict[int, list[Benefit]]:
    if not package_ids:
        return {}
    rows = db.execute(
        select(PackageBenefit.package_id, Benefit)
        .join(Benefit, Benefit.id == PackageBenefit.benefit_id)
        .where(
            PackageBenefit.package_id.in_(package_ids),
            Benefit.is_active.is_(True),
        )
    ).all()
    result: dict[int, list[Benefit]] = defaultdict(list)
    for package_id, benefit in rows:
        result[package_id].append(benefit)
    return result


def _load_consumption(
    db: Session, assignment_ids: list[int], first_day: date, next_first_day: date
) -> dict[int, dict[str, Decimal]]:
    if not assignment_ids:
        return {}
    rows = db.execute(
        select(
            ExpenseAllocation.employee_assignment_id,
            Expense.status,
            ExpenseAllocation.amount,
        )
        .join(Expense, Expense.id == ExpenseAllocation.expense_id)
        .where(
            ExpenseAllocation.employee_assignment_id.in_(assignment_ids),
            Expense.status.in_(("APPROVED", "PENDING")),
            Expense.expense_date >= first_day,
            Expense.expense_date < next_first_day,
        )
    ).all()

    result: dict[int, dict[str, Decimal]] = defaultdict(
        lambda: {"approved": _ZERO, "pending": _ZERO}
    )
    for assignment_id, status, amount in rows:
        if status == "APPROVED":
            result[assignment_id]["approved"] += amount
        else:
            result[assignment_id]["pending"] += amount
    return result


def _build_package(
    assignment: EmployeeAssignment,
    package: Package,
    benefits: list[Benefit],
    consumption: dict[str, Decimal],
    has_department_budget: bool,
) -> PackageBalance:
    if not has_department_budget:
        benefit_items = [
            BenefitBalance(
                benefit_id=benefit.id,
                benefit_name=benefit.name,
                is_basic=benefit.is_basic,
                consumed=_ZERO,
                available=_ZERO,
            )
            for benefit in benefits
        ]
        return PackageBalance(
            package_id=package.id,
            package_name=package.name,
            assigned=_ZERO,
            approved=_ZERO,
            pending=_ZERO,
            consumed=_ZERO,
            available=_ZERO,
            benefits=benefit_items,
        )

    assigned = _quantize(assignment.assigned_amount)
    approved = _quantize(consumption.get("approved", _ZERO))
    pending = _quantize(consumption.get("pending", _ZERO))
    consumed = _quantize(approved + pending)
    available = _quantize(assigned - consumed)

    benefit_items = [
        BenefitBalance(
            benefit_id=benefit.id,
            benefit_name=benefit.name,
            is_basic=benefit.is_basic,
            consumed=consumed,
            available=available,
        )
        for benefit in benefits
    ]

    return PackageBalance(
        package_id=package.id,
        package_name=package.name,
        assigned=assigned,
        approved=approved,
        pending=pending,
        consumed=consumed,
        available=available,
        benefits=benefit_items,
    )


def _aggregate_by_benefit(
    packages: list[PackageBalance],
) -> list[BenefitBalance]:
    aggregate: dict[int, BenefitBalance] = {}
    for package in packages:
        for benefit in package.benefits:
            if benefit.benefit_id in aggregate:
                agg = aggregate[benefit.benefit_id]
                agg.consumed = _quantize(agg.consumed + benefit.consumed)
                agg.available = _quantize(agg.available + benefit.available)
            else:
                aggregate[benefit.benefit_id] = BenefitBalance(
                    benefit_id=benefit.benefit_id,
                    benefit_name=benefit.benefit_name,
                    is_basic=benefit.is_basic,
                    consumed=benefit.consumed,
                    available=benefit.available,
                )
    return sorted(aggregate.values(), key=lambda b: b.benefit_name)


def _empty_response(period: date | None) -> EmployeeBalanceResponse:
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


def get_balance(db: Session, user_id: int) -> EmployeeBalanceResponse:
    current = _current_period(db)
    if current is None:
        return _empty_response(period=None)

    first_day, next_first_day = current

    assignments = _load_assignments(db, user_id)
    if not assignments:
        return _empty_response(period=first_day)

    budgeted_package_ids = _package_ids_with_department_budget(
        db, assignments, first_day
    )

    package_ids = [a.package_id for a in assignments]
    assignment_ids = [a.id for a in assignments]

    packages_by_id = {
        p.id: p
        for p in db.scalars(select(Package).where(Package.id.in_(package_ids)))
    }
    benefits_by_package = _load_benefits_by_package(db, package_ids)
    consumption_by_assignment = _load_consumption(
        db, assignment_ids, first_day, next_first_day
    )

    package_results: list[PackageBalance] = []
    for assignment in assignments:
        package = packages_by_id.get(assignment.package_id)
        if package is None or not package.is_active:
            continue
        package_results.append(
            _build_package(
                assignment,
                package,
                benefits_by_package.get(package.id, []),
                consumption_by_assignment.get(assignment.id, {}),
                has_department_budget=package.id in budgeted_package_ids,
            )
        )

    package_results.sort(key=lambda p: p.package_name)
    by_benefit = _aggregate_by_benefit(package_results)

    assigned_total = _quantize(sum((p.assigned for p in package_results), _ZERO))
    approved_total = _quantize(sum((p.approved for p in package_results), _ZERO))
    pending_total = _quantize(sum((p.pending for p in package_results), _ZERO))
    consumed_total = _quantize(approved_total + pending_total)
    available_total = _quantize(assigned_total - consumed_total)

    return EmployeeBalanceResponse(
        period=first_day,
        assigned_total=assigned_total,
        approved_total=approved_total,
        pending_total=pending_total,
        consumed_total=consumed_total,
        available_total=available_total,
        by_benefit=by_benefit,
        packages=package_results,
    )