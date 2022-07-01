"""module containing utility functions

functions:
    log_message"""

import logging
import sys
from logging import Logger
from datetime import datetime


def log_message(
    logger: Logger,
    msg: str,
    level: int = logging.INFO,
) -> None:
    """logs a message to the level specified in the logger with a
    timestamp

    Args:
        logger (Logger): the logger of the current module
        msg (str): the message to log
        level (int, optional): the int value of the log message.
            Defaults to logging.INFO.
    """
    msg = f"[{logger.name}] {datetime.now()} - {msg}"
    logger.log(level, msg)

    if level >= logging.ERROR:
        sys.exit(1)
