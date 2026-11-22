"""Modelo de la tabla benefit_budget_references (referencia informativa por beneficio)."""

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


class BenefitBudgetReference(Base):
    """Importe orientativo de un beneficio dentro de un presupuesto departamental.

    Es puramente informativo: no suma al presupuesto del departamento ni
    limita asignaciones ni gastos reales.
    """

    __tablename__ = "benefit_budget_references"
    __table_args__ = (
        ForeignKeyConstraint(
            ["department_budget_id"],
            ["department_budgets.id"],
            name="fk_benefit_budget_references_department_budget",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["benefit_id"],
            ["benefits.id"],
            name="fk_benefit_budget_references_benefit",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "department_budget_id",
            "benefit_id",
            name="uq_benefit_budget_references_department_benefit",
        ),
        CheckConstraint(
            "indicative_amount >= 0",
            name="ck_benefit_budget_references_indicative_amount",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    department_budget_id: Mapped[int]
    benefit_id: Mapped[int]
    indicative_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
