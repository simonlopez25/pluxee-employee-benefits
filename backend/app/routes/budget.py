"""Endpoints de presupuestos: /api/budgets (HU-11 / PEB-19)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.budget import (
    BenefitReferenceBulkUpdate,
    DepartmentBudgetResponse,
    DepartmentBudgetUpsert,
    GlobalBudgetResponse,
    GlobalBudgetUpsert,
    MonthlyBudgetOverview,
)
from app.services import budget_service

router = APIRouter(tags=["budgets"])

# Errores documentados en Swagger (cuerpo real de la respuesta)
_ERROR_CONFLICT = {
    "description": "409 - Conflicto de presupuesto (techo/suelo/global no creado)",
    "content": {
        "application/json": {
            "example": {
                "error": {
                    "code": "conflict",
                    "message": "No se puede reducir el presupuesto global a 5000.00: ya se repartieron 8000.00 entre los departamentos de 2026-11-01. Importe mínimo válido: 8000.00.",
                }
            }
        }
    },
}
_ERROR_NOT_FOUND = {
    "description": "404 - Recurso no encontrado",
    "content": {
        "application/json": {
            "example": {"error": {"code": "not_found", "message": "Department 42 not found"}}
        }
    },
}
_ERROR_VALIDATION = {
    "description": "422 - Datos no válidos",
    "content": {
        "application/json": {
            "example": {"detail": [{"msg": "Value error, El importe no puede ser negativo"}]}
        }
    },
}

PeriodQuery = Annotated[
    date | None,
    Query(
        description="Mes del presupuesto (cualquier día del mes; se normaliza al día 1). Por defecto, el día 1 del mes actual."
    ),
]


@router.get(
    "/budgets",
    response_model=MonthlyBudgetOverview,
    summary="Resumen de presupuestos de un mes",
    responses={422: _ERROR_VALIDATION},
)
def get_monthly_budget(
    period: PeriodQuery = None,
    db: Session = Depends(get_db),
    _= Depends(require_admin),
) -> MonthlyBudgetOverview:
    """Sin `period` usa el mes actual; un mes sin global devuelve ceros, sin error."""
    if period is None:
        period = budget_service.first_day(datetime.now().date())
    return budget_service.get_monthly_budget_overview(db, period)


@router.put(
    "/budgets/global",
    response_model=GlobalBudgetResponse,
    status_code=status.HTTP_200_OK,
    summary="Crea o actualiza el presupuesto mensual global",
    responses={409: _ERROR_CONFLICT, 422: _ERROR_VALIDATION},
)
def upsert_global_budget(
    payload: GlobalBudgetUpsert,
    db: Session = Depends(get_db),
    _= Depends(require_admin),
) -> GlobalBudgetResponse:
    """Crea o actualiza el global; 409 si bajaría de lo ya repartido (suelo)."""
    row = budget_service.upsert_global_budget(db, payload.period, payload.total_amount)
    return budget_service._global_budget_response(db, row)


@router.put(
    "/budgets/departments/{department_id}",
    response_model=DepartmentBudgetResponse,
    status_code=status.HTTP_200_OK,
    summary="Fija o actualiza el presupuesto mensual de un departamento",
    responses={404: _ERROR_NOT_FOUND, 409: _ERROR_CONFLICT, 422: _ERROR_VALIDATION},
)
def upsert_department_budget(
    department_id: Annotated[int, Path(description="Id del departamento")],
    payload: DepartmentBudgetUpsert,
    db: Session = Depends(get_db),
    _= Depends(require_admin),
) -> DepartmentBudgetResponse:
    """Fija el presupuesto de un departamento; 409 si no hay global o se excede el techo."""
    row = budget_service.upsert_department_budget(
        db, department_id, payload.period, payload.allocated_amount
    )
    return budget_service._department_budget_detail(db, row)


@router.put(
    "/budgets/departments/{department_id}/references",
    response_model=DepartmentBudgetResponse,
    status_code=status.HTTP_200_OK,
    summary="Guarda o actualiza las referencias orientativas por beneficio",
    responses={404: _ERROR_NOT_FOUND, 409: _ERROR_CONFLICT, 422: _ERROR_VALIDATION},
)
def upsert_benefit_references(
    department_id: Annotated[int, Path(description="Id del departamento")],
    payload: BenefitReferenceBulkUpdate,
    db: Session = Depends(get_db),
    _= Depends(require_admin),
) -> DepartmentBudgetResponse:
    """Guarda las referencias orientativas por beneficio (solo informativas)."""
    return budget_service.upsert_benefit_references(
        db, department_id, payload.period, payload.references
    )
