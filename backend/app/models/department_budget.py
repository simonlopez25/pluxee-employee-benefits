"""Modelo de la tabla department_budgets (presupuesto por departamento y mes)."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    ForeignKeyConstraint,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DepartmentBudget(Base):
    __tablename__ = "department_budgets"
    __table_args__ = (
        ForeignKeyConstraint(
            ["global_budget_id"],
            ["global_budgets.id"],
            name="fk_department_budgets_global",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
            name="fk_department_budgets_department",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "global_budget_id",
            "department_id",
            name="uq_department_budgets_global_department",
        ),
        CheckConstraint("amount >= 0", name="ck_department_budgets_amount"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    global_budget_id: Mapped[int]
    department_id: Mapped[int]
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
