"""Modelo de la tabla employee_assignments (paquetes de cada empleado)."""

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
            ["department_assignment_id"],
            ["department_assignments.id"],
            name="fk_employee_assignments_department_assignment",
            ondelete="RESTRICT",
        ),
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
            "department_assignment_id",
            "user_id",
            name="uq_employee_assignments_assignment_user",
        ),
        UniqueConstraint("id", "package_id", name="uq_employee_assignments_id_package"),
        # FK compuesta: el paquete es el mismo que el de la asignación del departamento
        ForeignKeyConstraint(
            ["department_assignment_id", "package_id"],
            ["department_assignments.id", "department_assignments.package_id"],
            name="fk_employee_assignments_assignment_package",
            ondelete="RESTRICT",
        ),
        CheckConstraint("assigned_amount >= 0", name="ck_employee_assignments_amount"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    department_assignment_id: Mapped[int]
    package_id: Mapped[int]
    user_id: Mapped[int]
    assigned_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())
