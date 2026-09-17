import sys
from functools import lru_cache
from loguru import logger


@lru_cache()
def get_logger(name: str = "app"):
    from app.core.config import get_settings

    settings = get_settings()
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        enqueue=True,
    )
    return logger.bind(name=name)
