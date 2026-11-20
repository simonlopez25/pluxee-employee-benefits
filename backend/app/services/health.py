"""Lógica de negocio del endpoint de salud."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import health as health_model
from app.schemas.health import HealthResponse


def get_health(db: Session) -> HealthResponse:
    """Estado del servidor y de la base de datos.

    Si PostgreSQL no está disponible, la BD reporta "down" pero el
    endpoint sigue respondiendo 200 (el servidor está vivo).
    """
    database = "up" if health_model.ping(db) else "down"
    return HealthResponse(status="ok", database=database)
