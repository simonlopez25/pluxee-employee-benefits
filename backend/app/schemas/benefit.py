"""Esquemas de entrada y salida del catálogo de beneficios."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# La columna benefits.name es VARCHAR(80) en la BD aprobada.
NAME_MAX_LENGTH = 80


def _clean_name(value: str) -> str:
    """Recorta el nombre y rechaza valores vacíos o demasiado largos."""
    name = value.strip()
    if not name:
        raise ValueError("El nombre no puede estar vacío")
    if len(name) > NAME_MAX_LENGTH:
        raise ValueError(f"El nombre no puede superar los {NAME_MAX_LENGTH} caracteres")
    return name


class BenefitBase(BaseModel):
    """Campos comunes de un beneficio."""

    name: str = Field(description="Nombre único del beneficio (ej. Comida, Transporte)")
    description: str | None = Field(
        default=None,
        description="Descripción del beneficio; se guarda vacía si no se envía",
    )
    is_basic: bool = Field(
        default=False,
        description="Indica si es un beneficio básico/esencial de la empresa",
    )

    @field_validator("name", mode="after")
    @classmethod
    def name_must_be_valid(cls, value: str) -> str:
        """Aplica trim y valida que el nombre no esté vacío."""
        return _clean_name(value)


class BenefitCreate(BenefitBase):
    """Payload de POST /api/benefits."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Comida",
                "description": (
                    "Gastos en restauración. El empleado pide el reembolso "
                    "con un ticket o factura y el importe gastado."
                ),
                "is_basic": True,
                "is_active": True,
            }
        }
    )

    is_active: bool = Field(
        default=True,
        description="Habilitado para nuevos paquetes/gastos",
    )


class BenefitUpdate(BaseModel):
    """Payload de PUT /api/benefits/{benefit_id}: campos completos o parciales.

    Los campos con null se ignoran (no se modifican).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Comida",
                "description": "Descripción actualizada del beneficio.",
                "is_basic": True,
                "is_active": True,
            }
        }
    )

    name: str | None = Field(default=None, description="Nuevo nombre del beneficio")
    description: str | None = Field(default=None, description="Nueva descripción")
    is_basic: bool | None = Field(default=None, description="Nuevo valor de is_basic")
    is_active: bool | None = Field(default=None, description="Nuevo valor de is_active")

    @field_validator("name", mode="after")
    @classmethod
    def name_must_be_valid(cls, value: str | None) -> str | None:
        """None significa 'no modificar'; si se envía, aplica las mismas reglas."""
        return _clean_name(value) if value is not None else None


class BenefitStatusUpdate(BaseModel):
    """Payload de PATCH /api/benefits/{benefit_id}: solo estado (baja lógica)."""

    model_config = ConfigDict(
        json_schema_extra={"example": {"is_active": False}}
    )

    is_active: bool | None = Field(default=None, description="Activa o desactiva el beneficio")
    is_basic: bool | None = Field(default=None, description="Marca o desmarca el beneficio como básico")

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> BenefitStatusUpdate:
        """Exige al menos un campo para evitar actualizaciones vacías."""
        if self.is_active is None and self.is_basic is None:
            raise ValueError("Debe indicar al menos un campo para actualizar")
        return self


class BenefitResponse(BaseModel):
    """Respuesta de los endpoints de beneficios."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Comida",
                "description": (
                    "Gastos en restauración. El empleado pide el reembolso "
                    "con un ticket o factura y el importe gastado."
                ),
                "is_basic": True,
                "is_active": True,
            }
        },
    )

    id: int = Field(description="Identificador único del beneficio")
    name: str = Field(description="Nombre único del beneficio")
    description: str = Field(description="Descripción del beneficio")
    is_basic: bool = Field(description="Beneficio básico de la empresa")
    is_active: bool = Field(description="Beneficio habilitado para nuevos paquetes/gastos")
