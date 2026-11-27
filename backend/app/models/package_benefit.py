from __future__ import annotations

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PackageBenefit(Base):
    __tablename__ = "package_benefits"
    __table_args__ = (
        PrimaryKeyConstraint("package_id", "benefit_id", name="pk_package_benefits"),
        ForeignKeyConstraint(
            ["package_id"],
            ["packages.id"],
            name="fk_package_benefits_package",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["benefit_id"],
            ["benefits.id"],
            name="fk_package_benefits_benefit",
            ondelete="RESTRICT",
        ),
    )

    package_id: Mapped[int] = mapped_column(primary_key=True)
    benefit_id: Mapped[int] = mapped_column(primary_key=True)
