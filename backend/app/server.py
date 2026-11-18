"""Arranque del servidor con uvicorn."""

from __future__ import annotations

import uvicorn

from app.core.config import settings


def main() -> None:
    """Levanta el servidor en el puerto configurado en .env."""
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=settings.port,
        reload=settings.app_env != "production",
    )


if __name__ == "__main__":
    main()
