"""Configuración de la aplicación (variables de entorno y .env).

Prioridad: variables del sistema > `backend/.env` > `../.env.local` de la
raíz (lo escribe la CLI de Neon) > valores por defecto DB_* (Postgres local).
"""

from __future__ import annotations

from pathlib import Path

from dotenv import dotenv_values
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL, make_url

# backend/ (config.py está en backend/app/core/)
BACKEND_ROOT = Path(__file__).resolve().parents[2]
# Raíz del monorepo: ahí escribe la CLI de Neon sus variables
REPO_ROOT = BACKEND_ROOT.parent
NEON_ENV_FILES = (REPO_ROOT / ".env.local", REPO_ROOT / ".env")


class Settings(BaseSettings):
    """Ajustes en runtime. Las variables de entorno tienen prioridad sobre .env."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    port: int = 4000
    cors_origins: str = "http://localhost:5173"
    
    # JWT (HU-03)
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 480

    # URL completas (Neon u override manual). Vacío => se construyen con DB_*.
    database_url: str = ""
    database_url_unpooled: str = ""

    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = ""
    db_name: str = "pluxee"

    @staticmethod
    def _neon_env_value(key: str) -> str:
        """DATABASE_URL[_UNPOOLED] escritas por `neon env pull`/`neon deploy`."""
        for path in NEON_ENV_FILES:
            if path.is_file():
                value = (dotenv_values(path).get(key) or "").strip()
                if value:
                    return value
        return ""

    @staticmethod
    def _to_engine_url(raw: str) -> URL:
        """Convierte una URL en texto a URL de SQLAlchemy para psycopg3.

        Neon exige TLS: si la URL no trae `sslmode`, se añade `require`
        cuando el host es de Neon (*.neon.tech).
        """
        url = make_url(raw)
        if url.drivername in {"postgresql", "postgres"}:
            url = url.set(drivername="postgresql+psycopg")
        if (url.host or "").endswith("neon.tech") and "sslmode" not in url.query:
            url = url.set(query={**url.query, "sslmode": "require"})
        return url

    @property
    def app_database_url(self) -> URL:
        """URL de la aplicación: pooled de Neon si existe; si no, DB_* locales.

        El pooler de Neon (PgBouncer, modo transacción) es el indicado para el
        tráfico normal de la app.
        """
        raw = self.database_url.strip() or self._neon_env_value("DATABASE_URL")
        if not raw:
            return URL.create(
                "postgresql+psycopg",
                username=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
            )
        return self._to_engine_url(raw)

    @property
    def migration_database_url(self) -> URL:
        """URL de Alembic: conexión directa (sin pooler).

        Las migraciones usan el endpoint directo porque el pooler (PgBouncer en
        modo transacción) no soporta operaciones de sesión. Si solo existe la
        pooled, se usa esa (igual sirve para consultas simples).
        """
        raw = (
            self.database_url_unpooled.strip()
            or self._neon_env_value("DATABASE_URL_UNPOOLED")
            or self.database_url.strip()
            or self._neon_env_value("DATABASE_URL")
        )
        if not raw:
            return self.app_database_url
        return self._to_engine_url(raw)

    @property
    def cors_origin_list(self) -> list[str]:
        """Orígenes CORS separados por coma."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
