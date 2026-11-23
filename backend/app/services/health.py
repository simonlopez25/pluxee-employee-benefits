"""Lógica de negocio del endpoint de salud."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import health as health_model
from app.schemas.health import HealthResponse


def get_health(db: Session) -> HealthResponse:
    """Estado del servidor; sin PostgreSQL responde 200 con database=down."""
    database = "up" if health_model.ping(db) else "down"
    return HealthResponse(status="ok", database=database)
