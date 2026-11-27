from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.budget_common import Money, first_day, validate_non_negative


class BenefitReferenceItem(BaseModel):
    benefit_id: int = Field(description="Identificador del beneficio")
    benefit_name: str = Field(description="Nombre del beneficio")
    indicative_amount: Money = Field(description="Importe orientativo (>= 0)")


class BenefitReferenceItemIn(BaseModel):
    benefit_id: int = Field(description="Identificador del beneficio")
    indicative_amount: Decimal = Field(
        ge=0, description="Importe orientativo del beneficio (>= 0)"
    )

    @field_validator("indicative_amount", mode="after")
    @classmethod
    def indicative_amount_must_be_non_negative(cls, value: Decimal) -> Decimal:
        return validate_non_negative(value, "importe orientativo")


class BenefitReferenceBulkUpdate(BaseModel):
    period: date = Field(description="Mes de las referencias (se normaliza al día 1)")
    references: list[BenefitReferenceItemIn] = Field(
        default_factory=list,
        description="Referencias orientativas por beneficio del departamento en ese mes",
    )

    @field_validator("period", mode="after")
    @classmethod
    def period_must_be_first_day(cls, value: date) -> date:
        return first_day(value)