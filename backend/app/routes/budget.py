"""Endpoints de presupuestos: /api/budgets (HU-11 / PEB-19).

Presupuestos en 2 niveles (global mensual + por departamento) y
referencias informativas por beneficio.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import (
    Department,
    DepartmentBudget,
    GlobalBudget,
)
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

# ---------------------------------------------------------------------
# Documentación de errores en Swagger (cuerpo real de la respuesta)
# ---------------------------------------------------------------------

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

# TODO (PEB-12): Inyectar dependencia de autorización para rol ADMIN
# en las rutas de escritura (PUT).

PeriodQuery = Annotated[
    date | None,
    Query(
        description="Mes del presupuesto (cualquier día del mes; se normaliza al día 1). Por defecto, el día 1 del mes actual."
    ),
]


def _today_first_day() -> date:
    today = datetime.now().date()
    return today.replace(day=1)


# ---------------------------------------------------------------------
# GET /api/budgets — resumen completo de un mes
# ---------------------------------------------------------------------

@router.get(
    "/budgets",
    response_model=MonthlyBudgetOverview,
    summary="Resumen de presupuestos de un mes",
    responses={422: _ERROR_VALIDATION},
)
def get_monthly_budget(
    period: PeriodQuery = None,
    db: Session = Depends(get_db),
) -> MonthlyBudgetOverview:
    """Devuelve el estado completo de presupuestos del mes.

    Si no se envía `period`, se usa el día 1 del mes actual. Si el mes
    aún no tiene presupuesto global, devuelve total_amount 0 sin error.
    """
    if period is None:
        period = _today_first_day()
    return budget_service.get_monthly_budget_overview(db, period)


# ---------------------------------------------------------------------
# PUT /api/budgets/global — presupuesto global mensual
# ---------------------------------------------------------------------

@router.put(
    "/budgets/global",
    response_model=GlobalBudgetResponse,
    status_code=status.HTTP_200_OK,
    summary="Crea o actualiza el presupuesto mensual global",
    responses={409: _ERROR_CONFLICT, 422: _ERROR_VALIDATION},
)
def upsert_global_budget(
    payload: GlobalBudgetUpsert, db: Session = Depends(get_db)
) -> GlobalBudgetResponse:
    """Crea o actualiza el presupuesto mensual global de un mes.

    Rechaza con 409 si el nuevo total es menor que lo ya repartido entre
    los departamentos de ese mes (regla de suelo).
    """
    # TODO (PEB-12): Inyectar dependencia de autorización para rol ADMIN
    row = budget_service.upsert_global_budget(db, payload.period, payload.total_amount)
    return budget_service._global_budget_response(db, row)


# ---------------------------------------------------------------------
# PUT /api/budgets/departments/{department_id} — presupuesto por departamento
# ---------------------------------------------------------------------

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
) -> DepartmentBudgetResponse:
    """Fija o actualiza el presupuesto mensual de un departamento en un mes.

    Rechaza con 409 si:
    - el departamento no existe o no está activo,
    - no existe presupuesto global para ese mes,
    - la nueva suma de departamentos excede el techo global (regla de techo).
    """
    # TODO (PEB-12): Inyectar dependencia de autorización para rol ADMIN
    row = budget_service.upsert_department_budget(
        db, department_id, payload.period, payload.allocated_amount
    )
    return budget_service._department_budget_detail(db, row)


# ---------------------------------------------------------------------
# PUT /api/budgets/departments/{department_id}/references — referencias por beneficio
# ---------------------------------------------------------------------

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
) -> DepartmentBudgetResponse:
    """Guarda o actualiza los importes orientativos (indicative_amount) por
    beneficio de un departamento y mes.

    Es estrictamente informativo: no suma al presupuesto del departamento,
    no exige que coincida con allocated_amount y no bloquea asignaciones ni
    gastos reales.
    """
    # TODO (PEB-12): Inyectar dependencia de autorización para rol ADMIN
    budget_service.upsert_benefit_references(
        db, department_id, payload.period, payload.references
    )

    # Devolver el detalle del departamento (con sus referencias actualizadas).
    period = budget_service._first_day(payload.period)
    global_budget = db.scalar(
        select(GlobalBudget).where(GlobalBudget.period == period)
    )
    department_budget = db.scalar(
        select(DepartmentBudget).where(
            DepartmentBudget.global_budget_id == global_budget.id,
            DepartmentBudget.department_id == department_id,
        )
    )
    return budget_service._department_budget_detail(db, department_budget)
