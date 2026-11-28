from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field, computed_field, field_validator
NAME_MAX_LENGTH = 100


class PackageCreate(BaseModel):
    name: str = Field(description="Nombre del paquete (único dentro de su departamento)")
    description: str | None = Field(default=None, description="Descripción opcional")
    default_amount: Decimal = Field(
        ge=0, max_digits=12, decimal_places=2,
        description="Importe mensual por empleado",
    )
    department_id: int = Field(gt=0, description="Departamento al que pertenece")
    benefit_ids: list[int] = Field(
        min_length=1,
        description="Beneficios cubiertos: 1 = un solo beneficio, 2+ = multibeneficio",
    )

    @field_validator("name", mode="after")
    @classmethod
    def name_must_be_valid(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("El nombre no puede estar vacío")
        if len(name) > NAME_MAX_LENGTH:
            raise ValueError(f"El nombre no puede superar los {NAME_MAX_LENGTH} caracteres")
        return name

    @field_validator("benefit_ids", mode="after")
    @classmethod
    def benefits_must_not_repeat(cls, value: list[int]) -> list[int]:
        if len(value) != len(set(value)):
            raise ValueError("Un beneficio no puede repetirse en el mismo paquete")
        return value

class PackageBenefitItem(BaseModel):
        id: int = Field(description="Id del beneficio")
        name: str = Field(description="Nombre del beneficio")

class PackageResponse(BaseModel):
        id: int = Field(description="Identificador del paquete")
        name: str = Field(description="Nombre del paquete")
        description: str | None = Field(description="Descripción del paquete")
        default_amount: Decimal = Field(description="Importe mensual por empleado")
        department_id: int = Field(description="Departamento al que pertenece")
        is_active: bool = Field(description="Paquete activo")
        benefits: list[PackageBenefitItem] = Field(description="Beneficios cubiertos")

        @computed_field
        @property
        def package_type(self) -> str:
            return "MONO" if len(self.benefits) == 1 else "MULTI"