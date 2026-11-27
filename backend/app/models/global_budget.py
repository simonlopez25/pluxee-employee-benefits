from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class GlobalBudget(Base):
    __tablename__ = "global_budgets"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_global_budgets_amount"),
        CheckConstraint(
            "EXTRACT(DAY FROM period) = 1", name="ck_global_budgets_period"
        ),
        UniqueConstraint("period", name="global_budgets_period_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    period: Mapped[date] = mapped_column(Date)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()"
    )
