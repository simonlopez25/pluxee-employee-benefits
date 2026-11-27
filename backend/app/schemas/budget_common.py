from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import PlainSerializer

Money = Annotated[
    Decimal,
    PlainSerializer(lambda v: f"{v:.2f}", return_type=str),
]


def first_day(value: date) -> date:
    return value.replace(day=1)


def validate_non_negative(value: Decimal, field_name: str) -> Decimal:
    if value < 0:
        raise ValueError(f"{field_name} cannot be negative")
    return value