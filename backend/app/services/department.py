"""Lógica de negocio de los departamentos."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models import department as department_model
from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate


def list_departments(db: Session) -> list[Department]:
    """Lista los departamentos ordenados por nombre."""
    return department_model.get_all(db)


def get_department(db: Session, department_id: int) -> Department:
    """Devuelve un departamento o lanza 404 si no existe."""
    department = department_model.get_by_id(db, department_id)
    if department is None:
        raise NotFoundError("El departamento no existe.")
    return department


def create_department(db: Session, data: DepartmentCreate) -> Department:
    """Crea un departamento con nombre único."""
    _ensure_name_is_available(db, data.name)
    department = Department(name=data.name, currency=data.currency)
    return department_model.save(db, department)


def update_department(
    db: Session, department_id: int, data: DepartmentUpdate
) -> Department:
    """Edita el nombre y la divisa de un departamento."""
    department = get_department(db, department_id)
    _ensure_name_is_available(db, data.name, ignored_id=department_id)
    department.name = data.name
    department.currency = data.currency
    return department_model.save(db, department)


def _ensure_name_is_available(
    db: Session, name: str, ignored_id: int | None = None
) -> None:
    """Lanza 409 si otro departamento ya usa ese nombre."""
    existing = department_model.get_by_name(db, name)
    if existing is not None and existing.id != ignored_id:
        raise ConflictError(department_model.NAME_TAKEN_MESSAGE)