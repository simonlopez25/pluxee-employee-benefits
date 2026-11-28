from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKeyConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ExpenseHistory(Base):
    __tablename__ = "expense_history"
    __table_args__ = (
        ForeignKeyConstraint(
            ["expense_id"],
            ["expenses.id"],
            name="fk_expense_history_expense",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["actor_id"],
            ["users.id"],
            name="fk_expense_history_actor",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "previous_status IN ('PENDING', 'APPROVED', 'REJECTED')",
            name="ck_expense_history_previous_status",
        ),
        CheckConstraint(
            "new_status IN ('PENDING', 'APPROVED', 'REJECTED')",
            name="ck_expense_history_new_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    expense_id: Mapped[int]
    actor_id: Mapped[int]
    previous_status: Mapped[str] = mapped_column(String(20))
    new_status: Mapped[str] = mapped_column(String(20))
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()"
    )
