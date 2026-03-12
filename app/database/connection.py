from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.config.settings import get_settings
from app.database.base import Base

settings = get_settings()

engine: AsyncEngine = create_async_engine(
    settings.postgres_async_dsn(),
    echo=settings.SQLALCHEMY_ECHO,
    pool_size=settings.SQLALCHEMY_POOL_SIZE,
    max_overflow=settings.SQLALCHEMY_MAX_OVERFLOW,
    future=True,
)


async def init_db() -> None:
    """Run database initialization (e.g. create tables for simple setups).

    In production, prefer Alembic migrations over create_all.
    Logs a warning and continues if the database is unreachable (e.g. wrong credentials).
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:  # e.g. InvalidPasswordError, connection refused
        import logging
        logging.getLogger(__name__).warning(
            "Database initialization skipped (could not connect): %s. "
            "Create a .env file in the project root with DATABASE_URL=postgresql://... or POSTGRES_* and ensure PostgreSQL is running.",
            e,
        )


