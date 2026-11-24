"""Endpoints de los paquetes de beneficios: /api/packages."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.package import PackageCreate, PackageResponse
from app.services import package_service

router = APIRouter(tags=["packages"])

# Errores documentados en Swagger (cuerpo real de la respuesta)
_ERROR_NOT_FOUND = {
    "description": "404 - Paquete, departamento o beneficio no encontrado",
    "content": {
        "application/json": {
            "example": {"error": {"code": "not_found", "message": "Paquete no encontrado"}}
        }
    },
}
_ERROR_CONFLICT = {
    "description": "409 - Nombre duplicado en el departamento",
    "content": {
        "application/json": {
            "example": {
                "error": {
                    "code": "conflict",
                    "message": "Ya existe un paquete con ese nombre en este departamento",
                }
            }
        }
    },
}

PackageIdPath = Annotated[int, Path(description="Id del paquete")]


@router.get(
    "/packages",
    response_model=list[PackageResponse],
    summary="Lista los paquetes",
)
def list_packages(
    department_id: Annotated[int | None, Query(description="Filtra por departamento")] = None,
    is_active: Annotated[bool | None, Query(description="Filtra por estado")] = None,
    db: Session = Depends(get_db),
) -> list[dict]:
    """Devuelve la lista de paquetes con sus beneficios."""
    return package_service.list_packages(db, department_id=department_id, is_active=is_active)


@router.get(
    "/packages/{package_id}",
    response_model=PackageResponse,
    summary="Obtiene un paquete",
    responses={404: _ERROR_NOT_FOUND},
)
def get_package(package_id: PackageIdPath, db: Session = Depends(get_db)) -> dict:
    """Devuelve un paquete por su id."""
    return package_service.get_package(db, package_id)


@router.post(
    "/packages",
    response_model=PackageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crea un paquete",
    responses={404: _ERROR_NOT_FOUND, 409: _ERROR_CONFLICT},
)
def create_package(payload: PackageCreate, db: Session = Depends(get_db)) -> dict:
    """Crea un paquete mono o multibeneficio para un departamento."""
    # TODO (PEB-12): Inyectar dependencia de autorización para rol ADMIN
    return package_service.create_package(db, payload)

