"""
core/utils/logger.py — DRY: shared logger for the entire project
"""
import logging
import os


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler()
        level = os.environ.get("LOG_LEVEL", "INFO").upper()
        h.setLevel(level)
        h.setFormatter(logging.Formatter(
            "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        logger.addHandler(h)
        logger.setLevel(level)
    return logger
