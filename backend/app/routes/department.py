"""Endpoints de departamentos: /api/departments."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.department import Department
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.services import department as department_service

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=list[DepartmentResponse])
def list_departments(db: Session = Depends(get_db)) -> list[Department]:
    """Lista todos los departamentos ordenados por nombre."""
    return department_service.list_departments(db)


@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(department_id: int, db: Session = Depends(get_db)) -> Department:
    """Devuelve un departamento por su identificador."""
    return department_service.get_department(db, department_id)


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    data: DepartmentCreate, db: Session = Depends(get_db)
) -> Department:
    """Crea un departamento con nombre único y divisa."""
    return department_service.create_department(db, data)


@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(
    department_id: int, data: DepartmentUpdate, db: Session = Depends(get_db)
) -> Department:
    """Edita el nombre y la divisa de un departamento."""
    return department_service.update_department(db, department_id, data)