"""Endpoints del catálogo de beneficios: /api/benefits."""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.benefit import Benefit
from app.schemas.benefit import (
    BenefitCreate,
    BenefitResponse,
    BenefitStatusUpdate,
    BenefitUpdate,
)
from app.services import benefit_service

router = APIRouter(tags=["benefits"])

# Errores documentados en Swagger (cuerpo real de la respuesta)
_ERROR_NOT_FOUND = {
    "description": "404 - Beneficio no encontrado",
    "content": {
        "application/json": {
            "example": {
                "error": {"code": "not_found", "message": "Beneficio no encontrado"}
            }
        }
    },
}
_ERROR_CONFLICT = {
    "description": "409 - Nombre duplicado",
    "content": {
        "application/json": {
            "example": {
                "error": {
                    "code": "conflict",
                    "message": "Ya existe un beneficio con ese nombre",
                }
            }
        }
    },
}
_ERROR_VALIDATION = {
    "description": "422 - Datos no válidos",
    "content": {
        "application/json": {
            "example": {"detail": [{"msg": "Value error, El nombre no puede estar vacío"}]}
        }
    },
}

BenefitIdPath = Annotated[int, Path(description="Id del beneficio")]


@router.get(
    "/benefits",
    response_model=list[BenefitResponse],
    summary="Lista los beneficios",
    responses={422: _ERROR_VALIDATION},
)
def list_benefits(
    is_active: Annotated[bool | None, Query(description="Filtra por estado")] = None,
    is_basic: Annotated[bool | None, Query(description="Filtra por tipo básico")] = None,
    order_by: Annotated[Literal["id", "name"], Query(description="Orden: id o name")] = "id",
    db: Session = Depends(get_db),
) -> list[Benefit]:
    """Devuelve la lista de beneficios."""
    return benefit_service.list_benefits(
        db,
        is_active=is_active,
        is_basic=is_basic,
        order_by=order_by,
    )


@router.get(
    "/benefits/{benefit_id}",
    response_model=BenefitResponse,
    summary="Obtiene un beneficio",
    responses={404: _ERROR_NOT_FOUND},
)
def get_benefit(benefit_id: BenefitIdPath, db: Session = Depends(get_db)) -> Benefit:
    """Devuelve un beneficio por su id."""
    return benefit_service.get_benefit(db, benefit_id)


@router.post(
    "/benefits",
    response_model=BenefitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crea un beneficio",
    responses={409: _ERROR_CONFLICT, 422: _ERROR_VALIDATION},
)
def create_benefit(payload: BenefitCreate, db: Session = Depends(get_db)) -> Benefit:
    """Crea un beneficio con nombre único."""
    return benefit_service.create_benefit(db, payload)


@router.put(
    "/benefits/{benefit_id}",
    response_model=BenefitResponse,
    summary="Actualiza un beneficio",
    responses={404: _ERROR_NOT_FOUND, 409: _ERROR_CONFLICT, 422: _ERROR_VALIDATION},
)
def update_benefit(
    benefit_id: BenefitIdPath,
    payload: BenefitUpdate,
    db: Session = Depends(get_db),
) -> Benefit:
    """Actualiza los campos enviados de un beneficio."""
    return benefit_service.update_benefit(db, benefit_id, payload)


@router.patch(
    "/benefits/{benefit_id}",
    response_model=BenefitResponse,
    summary="Activa o desactiva un beneficio",
    responses={404: _ERROR_NOT_FOUND, 422: _ERROR_VALIDATION},
)
def update_benefit_status(
    benefit_id: BenefitIdPath,
    payload: BenefitStatusUpdate,
    db: Session = Depends(get_db),
) -> Benefit:
    """Cambia el estado de un beneficio sin borrarlo."""
    return benefit_service.update_benefit_status(db, benefit_id, payload)
