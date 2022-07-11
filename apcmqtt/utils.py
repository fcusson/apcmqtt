"""module containing utility functions

functions:
    log_message"""

import logging
import sys
from logging import Logger
from datetime import datetime

LOGGER = logging.getLogger(__name__)


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
    msg = f"{datetime.now()} - {msg}"

    logger.log(level, msg)

    if level >= logging.ERROR:
        sys.exit(1)


def is_date(potential_date: str) -> bool:
    """validate if the potential_date is a string representation of a
    date

    Args:
        potential_date (str): a string that is potentially a
        representation of a date

    Returns:
        bool: True if potential_date represent a date
    """

    potential_date = potential_date.split(' ')[:2]
    potential_date = ' '.join(potential_date)

    try:
        log_message(
            LOGGER,
            f"checking if {potential_date} is a date",
            logging.DEBUG
        )
        datetime.strptime(potential_date, "%Y-%m-%d %H:%M:%S")
        return True
    except ValueError:
        return False
