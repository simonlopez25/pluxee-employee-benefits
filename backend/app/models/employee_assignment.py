"""Modelo de employee_assignments: paquete asignado a un empleado.

Un empleado tiene como mucho una asignación por paquete, con importe propio.
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKeyConstraint,
    Numeric,
    UniqueConstraint,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EmployeeAssignment(Base):
    __tablename__ = "employee_assignments"
    __table_args__ = (
        ForeignKeyConstraint(
            ["package_id"],
            ["packages.id"],
            name="fk_employee_assignments_package",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_employee_assignments_user",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "package_id",
            "user_id",
            name="uq_employee_assignments_package_user",
        ),
        # La usan las FK compuestas de expense_allocations
        UniqueConstraint("id", "package_id", name="uq_employee_assignments_id_package"),
        CheckConstraint("assigned_amount >= 0", name="ck_employee_assignments_amount"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    package_id: Mapped[int]
    user_id: Mapped[int]
    assigned_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())
