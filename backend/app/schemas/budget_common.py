"""Tipos comunes y validadores para schemas de presupuestos."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import PlainSerializer

# Siempre 2 decimales en las respuestas monetarias (coherente con NUMERIC(12,2)).
Money = Annotated[
    Decimal,
    PlainSerializer(lambda v: f"{v:.2f}", return_type=str),
]


def first_day(value: date) -> date:
    """Devuelve el día 1 del mes de la fecha recibida."""
    return value.replace(day=1)


def validate_non_negative(value: Decimal, field_name: str) -> Decimal:
    """Valida que un importe no sea negativo."""
    if value < 0:
        raise ValueError(f"El {field_name} no puede ser negativo")
    return value