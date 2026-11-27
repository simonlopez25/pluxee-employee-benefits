from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.schemas.package import PackageCreate, PackageResponse
from app.services import package_service

router = APIRouter(tags=["packages"])

_ERROR_NOT_FOUND = {
    "description": "404 - Package, department, or benefit not found",
    "content": {
        "application/json": {
            "example": {"error": {"code": "not_found", "message": "Package not found"}}
        }
    },
}
_ERROR_CONFLICT = {
    "description": "409 - Duplicate name in department",
    "content": {
        "application/json": {
            "example": {
                "error": {
                    "code": "conflict",
                    "message": "A package with that name already exists in this department",
                }
            }
        }
    },
}

PackageIdPath = Annotated[int, Path(description="Package ID")]


@router.get(
    "/packages",
    response_model=list[PackageResponse],
    summary="List packages",
)
def list_packages(
    department_id: Annotated[int | None, Query(description="Filter by department")] = None,
    is_active: Annotated[bool | None, Query(description="Filter by status")] = None,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    return package_service.list_packages(db, department_id=department_id, is_active=is_active)


@router.get(
    "/packages/{package_id}",
    response_model=PackageResponse,
    summary="Get a package",
    responses={404: _ERROR_NOT_FOUND},
)
def get_package(package_id: PackageIdPath, user=Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    return package_service.get_package(db, package_id)


@router.post(
    "/packages",
    response_model=PackageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a package",
    responses={404: _ERROR_NOT_FOUND, 409: _ERROR_CONFLICT},
)
def create_package(payload: PackageCreate, admin=Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    return package_service.create_package(db, payload)

