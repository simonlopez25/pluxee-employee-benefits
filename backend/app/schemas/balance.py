"""Schemas del saldo del empleado (HU-13 / PEB-55)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class BenefitBalance(BaseModel):
    """Saldo de un beneficio dentro de un paquete."""

    model_config = ConfigDict(from_attributes=True)

    benefit_id: int
    benefit_name: str
    is_basic: bool
    assigned: Decimal
    approved: Decimal
    pending: Decimal
    consumed: Decimal
    available: Decimal


class PackageBalance(BaseModel):
    """Paquete asignado al empleado con su desglose por beneficio."""

    model_config = ConfigDict(from_attributes=True)

    package_id: int
    package_name: str
    assigned: Decimal
    approved: Decimal
    pending: Decimal
    consumed: Decimal
    available: Decimal
    benefits: list[BenefitBalance]


class EmployeeBalanceResponse(BaseModel):
    """Resumen agregado + detalle de paquetes del empleado."""

    period: date | None
    assigned_total: Decimal
    approved_total: Decimal
    pending_total: Decimal
    consumed_total: Decimal
    available_total: Decimal
    by_benefit: list[BenefitBalance]
    packages: list[PackageBalance]