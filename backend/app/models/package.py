from __future__ import annotations

from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    Numeric,
    String,
    Text,
    text,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Package(Base):
    __tablename__ = "packages"
    __table_args__ = (
        ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
            name="fk_packages_department",
            ondelete="RESTRICT",
        ),
        CheckConstraint("default_amount >= 0", name="ck_packages_default_amount"),
        Index(
            "uq_package_name_department",
            "department_id",
            text("lower(name)"),
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    default_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    department_id: Mapped[int]
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())
