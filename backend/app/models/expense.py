from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKeyConstraint,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Expense(Base):
    __tablename__ = "expenses"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_expenses_user",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["benefit_id"],
            ["benefits.id"],
            name="fk_expenses_benefit",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["reviewed_by_id"],
            ["users.id"],
            name="fk_expenses_reviewed_by",
            ondelete="RESTRICT",
        ),
        CheckConstraint("amount > 0", name="ck_expenses_amount"),
        CheckConstraint(
            "status IN ('PENDING', 'APPROVED', 'REJECTED')", name="ck_expenses_status"
        ),
        CheckConstraint(
            "status <> 'REJECTED' OR rejection_reason IS NOT NULL",
            name="ck_expenses_rejection_reason",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    benefit_id: Mapped[int]
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    expense_date: Mapped[date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), server_default="PENDING")
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    reviewed_by_id: Mapped[int | None]
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()"
    )
