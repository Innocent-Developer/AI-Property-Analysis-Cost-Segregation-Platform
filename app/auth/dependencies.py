"""Optional auth: API key or JWT. Enable via AUTH_ENABLED and set API_KEY or JWT_SECRET in .env."""
from __future__ import annotations

from typing import Optional

from fastapi import Header, HTTPException, Request, status

from app.config.settings import get_settings


async def optional_api_key(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> Optional[str]:
    """Validate API key if AUTH_ENABLED and API_KEY are set; otherwise allow."""
    settings = get_settings()
    if not settings.AUTH_ENABLED or not settings.API_KEY:
        return None
    key = x_api_key or request.headers.get(settings.API_KEY_HEADER)
    if key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return key


def require_auth_dependency():
    """Return a dependency that enforces auth when AUTH_ENABLED; use in route dependencies."""
    return optional_api_key
