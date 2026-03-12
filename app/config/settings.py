from functools import lru_cache
from typing import Any, Dict, Optional

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresDsn(AnyUrl):
    allowed_schemes = {"postgres", "postgresql"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

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

    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "property_analysis"
    SQLALCHEMY_ECHO: bool = False
    SQLALCHEMY_POOL_SIZE: int = 10
    SQLALCHEMY_MAX_OVERFLOW: int = 20

    # Redis
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

    def postgres_dsn(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def postgres_async_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def redis_dsn(self) -> str:
        auth = ""
        if self.REDIS_PASSWORD or self.REDIS_USERNAME:
            user = self.REDIS_USERNAME or ""
            pwd = self.REDIS_PASSWORD or ""
            auth = f"{user}:{pwd}@"
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def celery_config(self) -> Dict[str, Any]:
        broker = self.CELERY_BROKER_URL or self.redis_dsn()
        backend = self.CELERY_RESULT_BACKEND or self.redis_dsn()
        return {
            "broker_url": broker,
            "result_backend": backend,
            "task_default_queue": self.CELERY_TASK_DEFAULT_QUEUE,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()

