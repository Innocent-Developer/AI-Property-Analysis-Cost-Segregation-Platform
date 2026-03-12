from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.database.session import get_db


router = APIRouter(tags=["health"])


@router.get("/health", summary="Health check")
async def health_check(db: AsyncSession = Depends(get_db)) -> dict:
    settings = get_settings()
    # Lightweight DB connectivity check
    await db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": settings.APP_VERSION,
    }

