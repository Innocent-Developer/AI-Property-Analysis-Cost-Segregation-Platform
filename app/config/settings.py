from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env from project root (parent of app/) so it works regardless of cwd
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _PROJECT_ROOT / ".env"


class PostgresDsn(AnyUrl):
    allowed_schemes = {"postgres", "postgresql"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE if _ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    APP_NAME: str = "AI Property Analysis & Cost Segregation API"
    APP_ENV: str = Field(default="development", description="Environment: development/staging/production")
    APP_DEBUG: bool = False
    APP_VERSION: str = "0.1.0"

    # Server
    API_PREFIX: str = "/api"
    BACKEND_CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins",
    )

    # Database (use DATABASE_URL for full URL, e.g. Render; otherwise POSTGRES_* are used)
    DATABASE_URL: Optional[str] = None
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "property_analysis"
    SQLALCHEMY_ECHO: bool = False
    SQLALCHEMY_POOL_SIZE: int = 10
    SQLALCHEMY_MAX_OVERFLOW: int = 20

    # Redis (set REDIS_URL for full URL e.g. Redis Labs; otherwise REDIS_HOST/PORT/DB/auth are used)
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_USERNAME: Optional[str] = None
    REDIS_PASSWORD: Optional[str] = None

    # Celery
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None
    CELERY_TASK_DEFAULT_QUEUE: str = "default"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False

    # Rate limiting (e.g. "200/minute")
    RATE_LIMIT_DEFAULT: str = "200/minute"

    # Auth (optional; set AUTH_ENABLED=true and JWT_SECRET or API_KEY to enable)
    AUTH_ENABLED: bool = False
    JWT_SECRET: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    API_KEY_HEADER: str = "X-API-Key"
    API_KEY: Optional[str] = None

    def postgres_dsn(self) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL.strip()
            if url.startswith("postgresql://"):
                return url.replace("postgresql://", "postgresql+psycopg2://", 1)
            if url.startswith("postgres://"):
                return url.replace("postgres://", "postgresql+psycopg2://", 1)
            return url
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def postgres_async_dsn(self) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL.strip()
            if url.startswith("postgresql://"):
                return url.replace("postgresql://", "postgresql+asyncpg://", 1)
            if url.startswith("postgres://"):
                return url.replace("postgres://", "postgresql+asyncpg://", 1)
            return url
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def redis_dsn(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL.strip()
        auth = ""
        if self.REDIS_PASSWORD or self.REDIS_USERNAME:
            user = self.REDIS_USERNAME or ""
            pwd = self.REDIS_PASSWORD or ""
            auth = f"{user}:{pwd}@"
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def celery_config(self) -> Dict[str, Any]:
        dsn = self.redis_dsn()
        broker = self.CELERY_BROKER_URL or dsn
        backend = self.CELERY_RESULT_BACKEND or dsn
        return {
            "broker_url": broker,
            "result_backend": backend,
            "task_default_queue": self.CELERY_TASK_DEFAULT_QUEUE,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()

