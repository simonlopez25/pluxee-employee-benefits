from __future__ import annotations

from sqlalchemy import Boolean, false, String, Text, UniqueConstraint, true
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Benefit(Base):
    __tablename__ = "benefits"
    __table_args__ = (
        UniqueConstraint("name", name="benefits_name_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(Text)
    is_basic: Mapped[bool] = mapped_column(Boolean, server_default=false())
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())
