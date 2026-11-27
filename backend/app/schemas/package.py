from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field, computed_field, field_validator
NAME_MAX_LENGTH = 100


class PackageCreate(BaseModel):
    name: str = Field(description="Package name (unique within its department)")
    description: str | None = Field(default=None, description="Optional description")
    default_amount: Decimal = Field(
        ge=0, max_digits=12, decimal_places=2,
        description="Monthly amount per employee",
    )
    department_id: int = Field(gt=0, description="Department it belongs to")
    benefit_ids: list[int] = Field(
        min_length=1,
        description="Benefits covered: 1 = single benefit, 2+ = multi-benefit",
    )

    @field_validator("name", mode="after")
    @classmethod
    def name_must_be_valid(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("Name cannot be empty")
        if len(name) > NAME_MAX_LENGTH:
            raise ValueError(f"Name cannot exceed {NAME_MAX_LENGTH} characters")
        return name

    @field_validator("benefit_ids", mode="after")
    @classmethod
    def benefits_must_not_repeat(cls, value: list[int]) -> list[int]:
        if len(value) != len(set(value)):
            raise ValueError("A benefit cannot be repeated in the same package")
        return value

class PackageBenefitItem(BaseModel):
        id: int = Field(description="Benefit ID")
        name: str = Field(description="Benefit name")

class PackageResponse(BaseModel):
        id: int = Field(description="Package identifier")
        name: str = Field(description="Package name")
        description: str | None = Field(description="Package description")
        default_amount: Decimal = Field(description="Monthly amount per employee")
        department_id: int = Field(description="Department it belongs to")
        is_active: bool = Field(description="Active package")
        benefits: list[PackageBenefitItem] = Field(description="Covered benefits")

        @computed_field
        @property
        def package_type(self) -> str:
            return "MONO" if len(self.benefits) == 1 else "MULTI"