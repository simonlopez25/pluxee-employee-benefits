"""Lógica de negocio de departamentos."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate

NAME_TAKEN_MESSAGE = "Ya existe un departamento con ese nombre."


def list_departments(
    db: Session, *, is_active: bool | None = None
) -> list[Department]:
    """Devuelve los departamentos ordenados por nombre, con filtro opcional de estado."""
    statement = select(Department).order_by(Department.name)
    if is_active is not None:
        statement = statement.where(Department.is_active == is_active)
    return list(db.scalars(statement).all())


def get_department(db: Session, department_id: int) -> Department:
    """Devuelve un departamento o lanza 404 si no existe."""
    department = db.get(Department, department_id)
    if department is None:
        raise NotFoundError("El departamento no existe.")
    return department


def create_department(db: Session, data: DepartmentCreate) -> Department:
    """Crea un departamento con nombre único."""
    _ensure_name_is_available(db, data.name)
    department = Department(name=data.name, currency=data.currency)
    return _save(db, department)


def update_department(
    db: Session, department_id: int, data: DepartmentUpdate
) -> Department:
    """Edita el nombre y la divisa de un departamento."""
    department = get_department(db, department_id)
    _ensure_name_is_available(db, data.name, ignored_id=department_id)
    department.name = data.name
    department.currency = data.currency
    return _save(db, department)


def _ensure_name_is_available(
    db: Session, name: str, ignored_id: int | None = None
) -> None:
    """Lanza 409 si otro departamento ya usa ese nombre, sin distinguir mayúsculas."""
    statement = select(Department.id).where(func.lower(Department.name) == name.lower())
    existing_id = db.scalars(statement).first()
    if existing_id is not None and existing_id != ignored_id:
        raise ConflictError(NAME_TAKEN_MESSAGE)


def _save(db: Session, department: Department) -> Department:
    """Guarda el departamento; la restricción única de la BD es la última defensa."""
    try:
        db.add(department)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ConflictError(NAME_TAKEN_MESSAGE) from error
    db.refresh(department)
    return department