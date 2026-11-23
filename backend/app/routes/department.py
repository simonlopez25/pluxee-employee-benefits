"""Endpoints de departamentos: /api/departments."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.department import Department
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)
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


@router.get(
    "/departments/{department_id}",
    response_model=DepartmentResponse,
    summary="Devuelve un departamento",
)
def get_department(department_id: int, db: Session = Depends(get_db)) -> Department:
    """Devuelve un departamento por su identificador."""
    return department_service.get_department(db, department_id)


@router.post(
    "/departments",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crea un departamento",
)
def create_department(
    data: DepartmentCreate, db: Session = Depends(get_db)
) -> Department:
    """Crea un departamento con nombre único y divisa."""
    return department_service.create_department(db, data)


@router.put(
    "/departments/{department_id}",
    response_model=DepartmentResponse,
    summary="Edita un departamento",
)
def update_department(
    department_id: int, data: DepartmentUpdate, db: Session = Depends(get_db)
) -> Department:
    """Edita el nombre y la divisa de un departamento."""
    return department_service.update_department(db, department_id, data)