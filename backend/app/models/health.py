from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


def ping(db: Session) -> bool:
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception:  # noqa: BLE001
        return False
