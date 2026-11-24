from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models.benefit import Benefit
from app.models.department import Department
from app.models.package import Package
from app.models.package_benefit import PackageBenefit
from app.schemas.package import PackageCreate

PACKAGE_NOT_FOUND = "Paquete no encontrado"
DEPARTMENT_NOT_FOUND = "Departamento no encontrado o inactivo"
BENEFIT_NOT_FOUND = "Uno o más beneficios no existen o están inactivos"
NAME_ALREADY_EXISTS = "Ya existe un paquete con ese nombre en este departamento"


def _get_active_department_or_404(db: Session, department_id: int) -> Department:
    """Devuelve el departamento si existe y está activo; si no, lanza 404."""
    department = db.get(Department, department_id)
    if department is None or not department.is_active:
        raise NotFoundError(DEPARTMENT_NOT_FOUND)
    return department


def _get_active_benefits_or_404(db: Session, benefit_ids: list[int]) -> list[Benefit]:
    """Devuelve los beneficios pedidos si todos existen y están activos; si no, 404."""
    statement = select(Benefit).where(
        Benefit.id.in_(benefit_ids),
        Benefit.is_active.is_(True),
    )
    benefits = list(db.scalars(statement).all())
    if len(benefits) != len(benefit_ids):
        raise NotFoundError(BENEFIT_NOT_FOUND)
    return benefits

def _ensure_name_is_available(db: Session, name: str, department_id: int) -> None:
    """Lanza 409 si el departamento ya tiene un paquete con ese nombre.

    No distingue mayúsculas: "Comida" y "comida" cuentan como el mismo nombre.
    """
    statement = select(Package.id).where(
        func.lower(Package.name) == name.lower(),
        Package.department_id == department_id,
    )
    if db.scalar(statement) is not None:
        raise ConflictError(NAME_ALREADY_EXISTS)


def create_package(db: Session, payload: PackageCreate) -> dict:
    """Crea un paquete y sus beneficios en una sola transacción."""
    _get_active_department_or_404(db, payload.department_id)
    benefits = _get_active_benefits_or_404(db, payload.benefit_ids)
    _ensure_name_is_available(db, payload.name, payload.department_id)

    package = Package(
        name=payload.name,
        description=payload.description,
        default_amount=payload.default_amount,
        department_id=payload.department_id,
    )
    db.add(package)
    try:
        db.flush()  # INSERT del paquete: ya tenemos package.id
        for benefit in benefits:
            db.add(PackageBenefit(package_id=package.id, benefit_id=benefit.id))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError(NAME_ALREADY_EXISTS) from None
    db.refresh(package)
    return _to_response(package, benefits)

def _to_response(package: Package, benefits: list[Benefit]) -> dict:

    return {
        "id": package.id,
        "name": package.name,
        "description": package.description,
        "default_amount": package.default_amount,
        "department_id": package.department_id,
        "is_active": package.is_active,
        "benefits": [{"id": benefit.id, "name": benefit.name} for benefit in benefits],
    }


def _get_package_benefits(db: Session, package_id: int) -> list[Benefit]:

    statement = (
        select(Benefit)
        .join(PackageBenefit, PackageBenefit.benefit_id == Benefit.id)
        .where(PackageBenefit.package_id == package_id)
        .order_by(Benefit.id)
    )
    return list(db.scalars(statement).all())


def get_package(db: Session, package_id: int) -> dict:

    package = db.get(Package, package_id)
    if package is None:
        raise NotFoundError(PACKAGE_NOT_FOUND)
    return _to_response(package, _get_package_benefits(db, package.id))


def list_packages(
    db: Session,
    *,
    department_id: int | None = None,
    is_active: bool | None = None,
) -> list[dict]:

    statement = select(Package)
    if department_id is not None:
        statement = statement.where(Package.department_id == department_id)
    if is_active is not None:
        statement = statement.where(Package.is_active == is_active)
    statement = statement.order_by(Package.id)

    packages = db.scalars(statement).all()
    return [_to_response(package, _get_package_benefits(db, package.id)) for package in packages]