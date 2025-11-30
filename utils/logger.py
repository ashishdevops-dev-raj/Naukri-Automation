# utils/logger.py
import logging
import sys
from logging import StreamHandler, Formatter

def setup_logger(name: str, level=logging.INFO):
    """
    Simple logger setup consistent across modules.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)

    handler = StreamHandler(sys.stdout)
    handler.setLevel(level)
    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handler.setFormatter(Formatter(fmt))
    logger.addHandler(handler)
    # Avoid duplicate logs if root logger configured elsewhere
    logger.propagate = False
    return logger
