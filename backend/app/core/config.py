from __future__ import annotations

from pathlib import Path

from dotenv import dotenv_values
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL, make_url

BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_ROOT.parent
NEON_ENV_FILES = (REPO_ROOT / ".env.local", REPO_ROOT / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    host: str = "127.0.0.1"
    port: int = 4000
    cors_origins: str = "http://localhost:5173"

    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 480

    database_url: str = ""
    database_url_unpooled: str = ""

    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = ""
    db_name: str = "pluxee"

    @staticmethod
    def _neon_env_value(key: str) -> str:
        for path in NEON_ENV_FILES:
            if path.is_file():
                value = (dotenv_values(path).get(key) or "").strip()
                if value:
                    return value
        return ""

    @staticmethod
    def _to_engine_url(raw: str) -> URL:
        url = make_url(raw)
        if url.drivername in {"postgresql", "postgres"}:
            url = url.set(drivername="postgresql+psycopg")
        if (url.host or "").endswith("neon.tech") and "sslmode" not in url.query:
            url = url.set(query={**url.query, "sslmode": "require"})
        return url

    @property
    def app_database_url(self) -> URL:
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
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
