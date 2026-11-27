from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.benefit import Benefit
from app.schemas.benefit import (
    BenefitCreate,
    BenefitResponse,
    BenefitStatusUpdate,
    BenefitUpdate,
)
from app.services import benefit_service

router = APIRouter(tags=["benefits"])

_ERROR_NOT_FOUND = {
    "description": "404 - Benefit not found",
    "content": {
        "application/json": {
            "example": {
                "error": {"code": "not_found", "message": "Benefit not found"}
            }
        }
    },
}
_ERROR_CONFLICT = {
    "description": "409 - Duplicate name",
    "content": {
        "application/json": {
            "example": {
                "error": {
                    "code": "conflict",
                    "message": "A benefit with that name already exists",
                }
            }
        }
    },
}
_ERROR_VALIDATION = {
    "description": "422 - Invalid data",
    "content": {
        "application/json": {
            "example": {"detail": [{"msg": "Value error, Name cannot be empty"}]}
        }
    },
}

BenefitIdPath = Annotated[int, Path(description="Benefit ID")]


@router.get(
    "/benefits",
    response_model=list[BenefitResponse],
    summary="List benefits",
    responses={422: _ERROR_VALIDATION},
)
def list_benefits(
    is_active: Annotated[bool | None, Query(description="Filter by status")] = None,
    is_basic: Annotated[bool | None, Query(description="Filter by basic type")] = None,
    order_by: Annotated[Literal["id", "name"], Query(description="Order: id or name")] = "id",
    db: Session = Depends(get_db),
    _= Depends(get_current_user),
) -> list[Benefit]:
    return benefit_service.list_benefits(
        db,
        is_active=is_active,
        is_basic=is_basic,
        order_by=order_by,
    )


@router.get(
    "/benefits/{benefit_id}",
    response_model=BenefitResponse,
    summary="Get a benefit",
    responses={404: _ERROR_NOT_FOUND},
)
def get_benefit(
    benefit_id: BenefitIdPath,
    db: Session = Depends(get_db),
    _= Depends(get_current_user),
) -> Benefit:
    return benefit_service.get_benefit(db, benefit_id)


@router.post(
    "/benefits",
    response_model=BenefitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a benefit",
    responses={409: _ERROR_CONFLICT, 422: _ERROR_VALIDATION},
)
def create_benefit(
    payload: BenefitCreate,
    db: Session = Depends(get_db),
    _= Depends(require_admin),
) -> Benefit:
    return benefit_service.create_benefit(db, payload)


@router.put(
    "/benefits/{benefit_id}",
    response_model=BenefitResponse,
    summary="Update a benefit",
    responses={404: _ERROR_NOT_FOUND, 409: _ERROR_CONFLICT, 422: _ERROR_VALIDATION},
)
def update_benefit(
    benefit_id: BenefitIdPath,
    payload: BenefitUpdate,
    db: Session = Depends(get_db),
    _= Depends(require_admin),
) -> Benefit:
    return benefit_service.update_benefit(db, benefit_id, payload)


@router.patch(
    "/benefits/{benefit_id}",
    response_model=BenefitResponse,
    summary="Enable or disable a benefit",
    responses={404: _ERROR_NOT_FOUND, 422: _ERROR_VALIDATION},
)
def update_benefit_status(
    benefit_id: BenefitIdPath,
    payload: BenefitStatusUpdate,
    db: Session = Depends(get_db),
    _= Depends(require_admin),
) -> Benefit:
    return benefit_service.update_benefit_status(db, benefit_id, payload)
