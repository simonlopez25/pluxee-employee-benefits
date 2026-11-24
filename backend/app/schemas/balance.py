"""Schemas del saldo del empleado (HU-13 / PEB-55)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class BenefitBalance(BaseModel):
    """Saldo agregado de un beneficio para el empleado.

    `available` es la suma del disponible de todos los paquetes que cubren
    el beneficio: si un paquete multibeneficio comparte saldo, un gasto en
    uno de sus beneficios reduce el disponible de todos ellos.
    """

    model_config = ConfigDict(from_attributes=True)

    benefit_id: int
    benefit_name: str
    is_basic: bool
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
    """Resumen agregado + detalle de paquetes del empleado.

    `assigned_total` es la suma de `assigned_amount` de los paquetes del
    empleado, no la suma de los disponibles por beneficio (que se solapan
    cuando un paquete multibeneficio cubre varios).
    """

    period: date | None
    assigned_total: Decimal
    approved_total: Decimal
    pending_total: Decimal
    consumed_total: Decimal
    available_total: Decimal
    by_benefit: list[BenefitBalance]
    packages: list[PackageBalance]