"""Acceso a datos del endpoint de salud."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


def ping(db: Session) -> bool:
    """Ejecuta SELECT 1. Devuelve True si PostgreSQL responde."""
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception:  # noqa: BLE001 — cualquier fallo de conexión cuenta como caída
        return False
