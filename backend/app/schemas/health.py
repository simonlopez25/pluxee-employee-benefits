"""Schema del endpoint de salud."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Respuesta de GET /api/health."""

    status: str = Field(description="Estado general del servidor")
    database: str = Field(description="Estado de la conexión a PostgreSQL: up | down")
