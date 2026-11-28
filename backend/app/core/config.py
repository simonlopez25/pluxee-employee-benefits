from __future__ import annotations

from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL, make_url

BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str
    host: str
    port: int
    cors_origins: str

    jwt_secret: str
    jwt_algorithm: str
    jwt_expires_minutes: int

    database_url: str = ""
    database_url_unpooled: str = ""

    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    @model_validator(mode="after")
    def validate_settings(self) -> Settings:
        if len(self.jwt_secret) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        if self.jwt_expires_minutes < 1:
            raise ValueError("JWT_EXPIRES_MINUTES must be a positive number")
        return self

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
        raw = self.database_url.strip()
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
            or self.database_url.strip()
        )
        if not raw:
            return self.app_database_url
        return self._to_engine_url(raw)

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
