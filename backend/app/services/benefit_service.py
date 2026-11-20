"""Lógica de negocio del catálogo de beneficios.

Reglas clave:
- El nombre es único sin distinguir mayúsculas/minúsculas.
- Nunca se borran registros: la baja es lógica (is_active = False),
  porque expenses, expense_allocations y package_benefits referencian
  benefits con ON DELETE RESTRICT.
"""

from __future__ import annotations

from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models.benefit import Benefit
from app.schemas.benefit import BenefitCreate, BenefitStatusUpdate, BenefitUpdate

BENEFIT_NOT_FOUND = "Beneficio no encontrado"
NAME_ALREADY_EXISTS = "Ya existe un beneficio con ese nombre"


def list_benefits(
    db: Session,
    *,
    is_active: bool | None = None,
    is_basic: bool | None = None,
    order_by: Literal["id", "name"] = "id",
) -> list[Benefit]:
    """Lista los beneficios ordenados, con filtros opcionales de estado."""
    statement = select(Benefit)

    if is_active is not None:
        statement = statement.where(Benefit.is_active == is_active)
    if is_basic is not None:
        statement = statement.where(Benefit.is_basic == is_basic)

    statement = statement.order_by(Benefit.id if order_by == "id" else Benefit.name)
    return list(db.scalars(statement).all())


def get_benefit(db: Session, benefit_id: int) -> Benefit:
    """Devuelve un beneficio por id o lanza 404."""
    return _get_or_404(db, benefit_id)


def create_benefit(db: Session, payload: BenefitCreate) -> Benefit:
    """Crea un beneficio validando que el nombre no esté duplicado."""
    _ensure_name_is_available(db, payload.name)

    benefit = Benefit(
        name=payload.name,
        # description es NOT NULL en la BD: ausente => cadena vacía
        description=payload.description or "",
        is_basic=payload.is_basic,
        is_active=payload.is_active,
    )
    return _save(db, benefit)


def update_benefit(db: Session, benefit_id: int, payload: BenefitUpdate) -> Benefit:
    """Actualiza los campos enviados (PUT); los campos ausentes no cambian."""
    benefit = _get_or_404(db, benefit_id)

    if payload.name is not None:
        _ensure_name_is_available(db, payload.name, exclude_id=benefit.id)
        benefit.name = payload.name
    if payload.description is not None:
        benefit.description = payload.description
    if payload.is_basic is not None:
        benefit.is_basic = payload.is_basic
    if payload.is_active is not None:
        benefit.is_active = payload.is_active

    return _save(db, benefit)


def update_benefit_status(
    db: Session,
    benefit_id: int,
    payload: BenefitStatusUpdate,
) -> Benefit:
    """Cambia is_active / is_basic sin tocar el resto (baja lógica, PATCH)."""
    benefit = _get_or_404(db, benefit_id)

    if payload.is_active is not None:
        benefit.is_active = payload.is_active
    if payload.is_basic is not None:
        benefit.is_basic = payload.is_basic

    return _save(db, benefit)


def _get_or_404(db: Session, benefit_id: int) -> Benefit:
    """Busca el beneficio o lanza el error 404 del módulo."""
    benefit = db.get(Benefit, benefit_id)
    if benefit is None:
        raise NotFoundError(BENEFIT_NOT_FOUND)
    return benefit


def _ensure_name_is_available(
    db: Session,
    name: str,
    *,
    exclude_id: int | None = None,
) -> None:
    """Lanza 409 si otro beneficio ya usa el nombre (ignorando mayúsculas)."""
    statement = select(Benefit.id).where(
        func.lower(Benefit.name) == name.strip().lower()
    )
    if exclude_id is not None:
        statement = statement.where(Benefit.id != exclude_id)

    if db.scalar(statement) is not None:
        raise ConflictError(NAME_ALREADY_EXISTS)


def _save(db: Session, benefit: Benefit) -> Benefit:
    """Añade, persiste y refresca el beneficio.

    El UNIQUE de benefits.name es la última línea de defensa ante
    condiciones de carrera: cualquier IntegrityError se traduce en 409.
    """
    db.add(benefit)  # en create es un INSERT; en update es un no-op
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError(NAME_ALREADY_EXISTS) from None
    db.refresh(benefit)
    return benefit
