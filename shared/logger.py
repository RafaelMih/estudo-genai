import logging
from rich.logging import RichHandler


def get_logger(name: str) -> logging.Logger:
    """Return a logger with Rich formatting. Call once per module."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = RichHandler(rich_tracebacks=True, markup=True)
        handler.setFormatter(logging.Formatter("%(message)s", datefmt="[%X]"))
        logger.addHandler(handler)

    try:
        from shared.config import settings
        logger.setLevel(settings.log_level.upper())
    except Exception:
        logger.setLevel("INFO")

    return logger
