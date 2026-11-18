"""Modelo de la tabla department_assignments (paquetes por departamento y mes)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Numeric,
    UniqueConstraint,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DepartmentAssignment(Base):
    __tablename__ = "department_assignments"
    __table_args__ = (
        ForeignKeyConstraint(
            ["department_budget_id"],
            ["department_budgets.id"],
            name="fk_department_assignments_budget",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["package_id"],
            ["packages.id"],
            name="fk_department_assignments_package",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "department_budget_id",
            "package_id",
            name="uq_department_assignments_budget_package",
        ),
        UniqueConstraint("id", "package_id", name="uq_department_assignments_id_package"),
        CheckConstraint(
            "amount_per_employee >= 0", name="ck_department_assignments_amount"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    department_budget_id: Mapped[int]
    package_id: Mapped[int]
    amount_per_employee: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())
