from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

NAME_MAX_LENGTH = 80


def _clean_name(value: str) -> str:
    name = value.strip()
    if not name:
        raise ValueError("El nombre no puede estar vacío")
    if len(name) > NAME_MAX_LENGTH:
        raise ValueError(f"El nombre no puede superar los {NAME_MAX_LENGTH} caracteres")
    return name


class BenefitBase(BaseModel):
    name: str = Field(description="Unique benefit name (e.g., Meal, Transport)")
    description: str | None = Field(
        default=None,
        description="Benefit description; stored empty if not provided",
    )
    is_basic: bool = Field(
        default=False,
        description="Indicates if it is a basic/essential company benefit",
    )

    @field_validator("name", mode="after")
    @classmethod
    def name_must_be_valid(cls, value: str) -> str:
        return _clean_name(value)


class BenefitCreate(BenefitBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Meal",
                "description": (
                    "Restaurant expenses. Employee requests reimbursement "
                    "with a ticket or invoice and the amount spent."
                ),
                "is_basic": True,
                "is_active": True,
            }
        }
    )

    is_active: bool = Field(
        default=True,
        description="Enabled for new packages/expenses",
    )


class BenefitUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Meal",
                "description": "Updated benefit description.",
                "is_basic": True,
                "is_active": True,
            }
        }
    )

    name: str | None = Field(default=None, description="New benefit name")
    description: str | None = Field(default=None, description="New description")
    is_basic: bool | None = Field(default=None, description="New is_basic value")
    is_active: bool | None = Field(default=None, description="New is_active value")

    @field_validator("name", mode="after")
    @classmethod
    def name_must_be_valid(cls, value: str | None) -> str | None:
        return _clean_name(value) if value is not None else None


class BenefitStatusUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"is_active": False}}
    )

    is_active: bool | None = Field(default=None, description="Enable or disable the benefit")
    is_basic: bool | None = Field(default=None, description="Mark or unmark benefit as basic")

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> BenefitStatusUpdate:
        if self.is_active is None and self.is_basic is None:
            raise ValueError("Se debe proporcionar al menos un campo")
        return self


class BenefitResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Meal",
                "description": (
                    "Restaurant expenses. The employee requests reimbursement "
                    "with a ticket or invoice and the amount spent."
                ),
                "is_basic": True,
                "is_active": True,
            }
        },
    )

    id: int = Field(description="Unique benefit identifier")
    name: str = Field(description="Unique benefit name")
    description: str = Field(description="Benefit description")
    is_basic: bool = Field(description="Basic company benefit")
    is_active: bool = Field(description="Benefit enabled for new packages/expenses")
