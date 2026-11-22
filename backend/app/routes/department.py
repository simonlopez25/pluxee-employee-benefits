"""Endpoint de departamentos: GET /api/departments."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.department import Department
from app.schemas.department import DepartmentResponse
from app.services import department_service

router = APIRouter(tags=["departments"])


@router.get(
    "/departments",
    response_model=list[DepartmentResponse],
    summary="Lista los departamentos",
)
def list_departments(
    is_active: Annotated[
        bool | None, Query(description="Filtra por estado; sin filtro devuelve todos")
    ] = None,
    db: Session = Depends(get_db),
) -> list[Department]:
    """Devuelve los departamentos ordenados por nombre."""
    return department_service.list_departments(db, is_active=is_active)
