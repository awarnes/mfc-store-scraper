"""Logging configuration using loguru."""
import sys

from loguru import logger

from src.azure.settings import settings

# Remove default handler
logger.remove()

# Add custom handler with format that includes module and line numbers
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level,
    colorize=True,
)

# Optional: Add file handler for persistent logs
# logger.add(
#     "logs/azure_{time}.log",
#     rotation="500 MB",
#     retention="10 days",
#     level=settings.log_level,
#     format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} - {message}",
# )

__all__ = ["logger"]
