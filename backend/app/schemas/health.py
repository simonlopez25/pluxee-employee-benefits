from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(description="Estado general del servidor")
    database: str = Field(description="Estado de la conexión a PostgreSQL: up | down")
