from fastapi import APIRouter
from sqlalchemy import text

from app.config.settings import get_settings
from app.database.session import AsyncSessionLocal


router = APIRouter(tags=["health"])


@router.get("/health", summary="Health check")
async def health_check() -> dict:
    settings = get_settings()
    database = "unavailable"
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        database = "connected"
    except Exception:
        pass
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": settings.APP_VERSION,
        "database": database,
    }

