"""Logger for the project."""

import logging
import os

from rich.logging import RichHandler

FORMAT = "%(message)s"
LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG")
DATEFMT = "[%X]"

logging.basicConfig(
    level=LEVEL, format=FORMAT, datefmt=DATEFMT, handlers=[RichHandler()]
)
logger = logging.getLogger("rich")
