"""Modelo de la tabla expense_allocations (reparto del gasto entre paquetes)."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ExpenseAllocation(Base):
    __tablename__ = "expense_allocations"
    __table_args__ = (
        ForeignKeyConstraint(
            ["expense_id"],
            ["expenses.id"],
            name="fk_expense_allocations_expense",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["employee_assignment_id"],
            ["employee_assignments.id"],
            name="fk_expense_allocations_employee_assignment",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["package_id"],
            ["packages.id"],
            name="fk_expense_allocations_package",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["benefit_id"],
            ["benefits.id"],
            name="fk_expense_allocations_benefit",
            ondelete="RESTRICT",
        ),
        # FK compuesta: el paquete es del empleado
        ForeignKeyConstraint(
            ["employee_assignment_id", "package_id"],
            ["employee_assignments.id", "employee_assignments.package_id"],
            name="fk_expense_allocations_assignment_package",
            ondelete="RESTRICT",
        ),
        # FK compuesta: el paquete cubre ese beneficio
        ForeignKeyConstraint(
            ["package_id", "benefit_id"],
            ["package_benefits.package_id", "package_benefits.benefit_id"],
            name="fk_expense_allocations_package_benefit",
            ondelete="RESTRICT",
        ),
        CheckConstraint("amount > 0", name="ck_expense_allocations_amount"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    expense_id: Mapped[int]
    employee_assignment_id: Mapped[int]
    package_id: Mapped[int]
    benefit_id: Mapped[int]
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
