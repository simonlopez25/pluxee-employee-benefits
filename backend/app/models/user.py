"""Modelo de la tabla users (administradores y empleados)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    String,
    Text,
    UniqueConstraint,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
            name="fk_users_department",
            ondelete="RESTRICT",
        ),
        CheckConstraint("role IN ('ADMIN', 'EMPLOYEE')", name="ck_users_role"),
        CheckConstraint(
            "(role = 'ADMIN' AND department_id IS NULL) OR "
            "(role = 'EMPLOYEE' AND department_id IS NOT NULL)",
            name="ck_users_role_department",
        ),
        UniqueConstraint("email", name="users_email_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[int | None]
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(150))
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(20))
    must_change_password: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=true()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())
    deactivated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()"
    )
