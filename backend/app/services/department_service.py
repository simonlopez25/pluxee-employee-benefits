"""Lógica de negocio de departamentos."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.department import Department


def list_departments(
    db: Session, *, is_active: bool | None = None
) -> list[Department]:
    """Devuelve los departamentos ordenados por nombre, con filtro opcional de estado."""
    statement = select(Department).order_by(Department.name)
    if is_active is not None:
        statement = statement.where(Department.is_active == is_active)
    return list(db.scalars(statement).all())
