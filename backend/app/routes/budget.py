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

_ERROR_CONFLICT = {
    "description": "409 - Budget conflict (ceiling/floor/global not created)",
    "content": {
        "application/json": {
            "example": {
                "error": {
                    "code": "conflict",
                    "message": "Cannot reduce global budget to 5000.00: 8000.00 already allocated across departments for 2026-11-01. Minimum valid amount: 8000.00.",
                }
            }
        }
    },
}
_ERROR_NOT_FOUND = {
    "description": "404 - Resource not found",
    "content": {
        "application/json": {
            "example": {"error": {"code": "not_found", "message": "Department 42 not found"}}
        }
    },
}
_ERROR_VALIDATION = {
    "description": "422 - Invalid data",
    "content": {
        "application/json": {
            "example": {"detail": [{"msg": "Value error, Amount cannot be negative"}]}
        }
    },
}

PeriodQuery = Annotated[
    date | None,
    Query(
        description="Budget month (any day of the month; normalized to day 1). Defaults to first day of current month."
    ),
]


@router.get(
    "/budgets",
    response_model=MonthlyBudgetOverview,
    summary="Monthly budget overview",
    responses={422: _ERROR_VALIDATION},
)
def get_monthly_budget(
    period: PeriodQuery = None,
    db: Session = Depends(get_db),
    _= Depends(require_admin),
) -> MonthlyBudgetOverview:
    if period is None:
        period = budget_service.first_day(datetime.now().date())
    return budget_service.get_monthly_budget_overview(db, period)


@router.put(
    "/budgets/global",
    response_model=GlobalBudgetResponse,
    status_code=status.HTTP_200_OK,
    summary="Create or update global monthly budget",
    responses={409: _ERROR_CONFLICT, 422: _ERROR_VALIDATION},
)
def upsert_global_budget(
    payload: GlobalBudgetUpsert,
    db: Session = Depends(get_db),
    _= Depends(require_admin),
) -> GlobalBudgetResponse:
    row = budget_service.upsert_global_budget(db, payload.period, payload.total_amount)
    return budget_service._global_budget_response(db, row)


@router.put(
    "/budgets/departments/{department_id}",
    response_model=DepartmentBudgetResponse,
    status_code=status.HTTP_200_OK,
    summary="Set or update department monthly budget",
    responses={404: _ERROR_NOT_FOUND, 409: _ERROR_CONFLICT, 422: _ERROR_VALIDATION},
)
def upsert_department_budget(
    department_id: Annotated[int, Path(description="Id del departamento")],
    payload: DepartmentBudgetUpsert,
    db: Session = Depends(get_db),
    _= Depends(require_admin),
) -> DepartmentBudgetResponse:
    row = budget_service.upsert_department_budget(
        db, department_id, payload.period, payload.allocated_amount
    )
    return budget_service._department_budget_detail(db, row)


@router.put(
    "/budgets/departments/{department_id}/references",
    response_model=DepartmentBudgetResponse,
    status_code=status.HTTP_200_OK,
    summary="Save or update benefit reference amounts",
    responses={404: _ERROR_NOT_FOUND, 409: _ERROR_CONFLICT, 422: _ERROR_VALIDATION},
)
def upsert_benefit_references(
    department_id: Annotated[int, Path(description="Id del departamento")],
    payload: BenefitReferenceBulkUpdate,
    db: Session = Depends(get_db),
    _= Depends(require_admin),
) -> DepartmentBudgetResponse:
    return budget_service.upsert_benefit_references(
        db, department_id, payload.period, payload.references
    )
