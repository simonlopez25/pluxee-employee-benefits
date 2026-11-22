"""Modelo de la tabla departments (departamentos de la plantilla)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import CHAR, Boolean, DateTime, String, UniqueConstraint, func, select, true
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, Session, mapped_column
from app.core.database import Base
from app.core.errors import ConflictError

NAME_TAKEN_MESSAGE = "Ya existe un departamento con ese nombre."


class Department(Base):
    __tablename__ = "departments"
    __table_args__ = (
        UniqueConstraint("name", name="departments_name_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    currency: Mapped[str] = mapped_column(CHAR(3), server_default="EUR")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()"
    )


def get_all(db: Session) -> list[Department]:
    """Todos los departamentos ordenados por nombre."""
    return list(db.scalars(select(Department).order_by(Department.name)))


def get_by_id(db: Session, department_id: int) -> Department | None:
    """Un departamento por su identificador, o None si no existe."""
    return db.get(Department, department_id)


def get_by_name(db: Session, name: str) -> Department | None:
    """Un departamento por su nombre, sin distinguir mayúsculas."""
    statement = select(Department).where(func.lower(Department.name) == name.lower())
    return db.scalars(statement).first()


def save(db: Session, department: Department) -> Department:
    """Guarda el departamento; la restricción única de la BD es la última defensa."""
    try:
        db.add(department)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ConflictError(NAME_TAKEN_MESSAGE) from error
    db.refresh(department)
    return department
