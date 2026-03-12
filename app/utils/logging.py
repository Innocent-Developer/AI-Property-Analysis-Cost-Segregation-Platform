import logging
import sys
from typing import Any, Dict

from loguru import logger

from app.config.settings import get_settings


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - thin adapter
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        logger.bind().opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def setup_logging() -> None:
    settings = get_settings()

    logging.root.handlers = []
    logging.root.setLevel(settings.LOG_LEVEL)

    handler = InterceptHandler()
    logging.basicConfig(handlers=[handler], level=settings.LOG_LEVEL, force=True)

    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    serialize = settings.LOG_JSON
    logger.add(sys.stdout, level=settings.LOG_LEVEL, format=log_format, serialize=serialize, backtrace=True, diagnose=False)


def get_log_extra(extra: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return extra or {}

