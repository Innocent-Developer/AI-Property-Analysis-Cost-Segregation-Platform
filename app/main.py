from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from app.config.settings import get_settings
from app.database.connection import init_db
from app.routes import api_router
from app.utils.logging import setup_logging

try:
    from slowapi import Limiter
    from slowapi.errors import RateLimitExceeded
except ImportError:
    Limiter = None
    RateLimitExceeded = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.APP_DEBUG,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if Limiter is not None:
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[settings.RATE_LIMIT_DEFAULT],
        )
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    else:
        limiter = None

    app.include_router(api_router, prefix=settings.API_PREFIX)

    return app


app = create_app()

