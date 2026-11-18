"""Entorno de Alembic.

Conecta las migraciones con la configuración del backend:
- URL de BD desde app/core/config.py (.env) — nunca desde alembic.ini
  (evita que configparser escape caracteres especiales de la contraseña)
- target_metadata desde app/core/database.py (Base) para autogenerate
"""

from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import create_engine, pool

from alembic import context

# backend/ en el sys.path para poder importar "app.*"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings  # noqa: E402
from app.core.database import Base  # noqa: E402
from app import models  # noqa: F401 — registra las 14 tablas en Base.metadata

# Este es el objeto Alembic Config, que da acceso a los valores del .ini
config = context.config

# Logging (formatea la salida de alembic)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Modelos detectados por `alembic revision --autogenerate`
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Corre migraciones en modo offline (genera SQL sin conectar a la BD)."""
    context.configure(
        url=str(settings.database_url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Corre migraciones en modo online (conecta a PostgreSQL)."""
    # Engine creado directamente desde settings (.env), sin pasar por alembic.ini
    connectable = create_engine(settings.database_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Detecta también cambios de tipo/nullable/defaults
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
