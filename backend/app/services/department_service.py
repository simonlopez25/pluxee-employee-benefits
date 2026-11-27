from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models.department import Department
from app.models.package import Package
from app.models.user import User
from app.schemas.department import (
    DepartmentCreate,
    DepartmentListResponse,
    DepartmentPackageSummary,
    DepartmentUpdate,
)

NAME_TAKEN_MESSAGE = "A department with that name already exists."


def list_departments(
    db: Session, *, is_active: bool | None = None
) -> list[DepartmentListResponse]:
    statement = select(Department).order_by(Department.name)
    if is_active is not None:
        statement = statement.where(Department.is_active == is_active)
    departments = list(db.scalars(statement).all())

    if not departments:
        return []

    dept_ids = [dept.id for dept in departments]

    employee_counts_rows = db.execute(
        select(User.department_id, func.count(User.id))
        .where(
            User.department_id.in_(dept_ids),
            User.role == "EMPLOYEE",
            User.is_active.is_(True),
        )
        .group_by(User.department_id)
    ).all()
    employee_count_by_dept: dict[int, int] = {
        dept_id: int(count)
        for dept_id, count in employee_counts_rows
        if dept_id is not None
    }

    active_package_rows = db.execute(
        select(Package.id, Package.name, Package.department_id)
        .where(
            Package.department_id.in_(dept_ids),
            Package.is_active.is_(True),
        )
        .order_by(Package.id)
    ).all()
    packages_by_dept: dict[int, list[DepartmentPackageSummary]] = {
        dept_id: [] for dept_id in dept_ids
    }
    for pkg_id, pkg_name, pkg_dept_id in active_package_rows:
        if pkg_dept_id in packages_by_dept:
            packages_by_dept[pkg_dept_id].append(
                DepartmentPackageSummary(id=pkg_id, name=pkg_name)
            )

    return [
        DepartmentListResponse(
            id=dept.id,
            name=dept.name,
            currency=dept.currency,
            is_active=dept.is_active,
            created_at=dept.created_at,
            employee_count=employee_count_by_dept.get(dept.id, 0),
            packages=packages_by_dept.get(dept.id, []),
        )
        for dept in departments
    ]


def get_department(db: Session, department_id: int) -> Department:
    department = db.get(Department, department_id)
    if department is None:
        raise NotFoundError("Department does not exist.")
    return department


def create_department(db: Session, data: DepartmentCreate) -> Department:
    _ensure_name_is_available(db, data.name)
    department = Department(name=data.name, currency=data.currency)
    return _save(db, department)


def update_department(
    db: Session, department_id: int, data: DepartmentUpdate
) -> Department:
    department = get_department(db, department_id)
    _ensure_name_is_available(db, data.name, ignored_id=department_id)
    department.name = data.name
    department.currency = data.currency
    return _save(db, department)


def _ensure_name_is_available(
    db: Session, name: str, ignored_id: int | None = None
) -> None:
    statement = select(Department.id).where(func.lower(Department.name) == name.lower())
    existing_id = db.scalars(statement).first()
    if existing_id is not None and existing_id != ignored_id:
        raise ConflictError(NAME_TAKEN_MESSAGE)


def _save(db: Session, department: Department) -> Department:
    try:
        db.add(department)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ConflictError(NAME_TAKEN_MESSAGE) from error
    db.refresh(department)
    return department