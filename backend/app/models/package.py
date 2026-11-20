"""Modelo de la tabla packages (paquetes de beneficios)."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Numeric, String, Text, UniqueConstraint, true
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Package(Base):
    __tablename__ = "packages"
    __table_args__ = (
        CheckConstraint("default_amount >= 0", name="ck_packages_default_amount"),
        UniqueConstraint("name", name="packages_name_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    default_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())
