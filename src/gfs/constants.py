import logging
import os

logger = logging.getLogger(__name__)


def get_logging_level() -> int:
    level = (os.getenv("LOGGING") or "INFO").upper()
    if not hasattr(logging, level):
        logger.warning(f"Invalid log level {level}. Defaulting to INFO.")
        return logging.INFO
    return getattr(logging, level)


VERSION = "0.1.0"

DIRECTORY_PROJECT_ROOT = "src/gfs/projects"

LEAF_BIT_DEPTH_RANGE = 10
