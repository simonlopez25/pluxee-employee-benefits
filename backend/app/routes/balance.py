"""Endpoint del saldo del empleado: /api/balance/me (HU-13 / PEB-55)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.balance import EmployeeBalanceResponse
from app.services import balance_service

router = APIRouter(tags=["balance"])


@router.get(
    "/balance/me",
    response_model=EmployeeBalanceResponse,
    summary="Saldo disponible del empleado",
)
def get_my_balance(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EmployeeBalanceResponse:
    """Devuelve el saldo agregado por beneficio y el detalle de paquetes."""
    return balance_service.get_balance(db, user.id)