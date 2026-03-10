"""Logging configuration for valkyrie-tools.

Provides a thin wrapper around :mod:`logging` that maps a CLI verbosity count
(number of ``-v`` flags) to a :mod:`logging` level and sets up a
:class:`~logging.StreamHandler` with a consistent format.

Module-level constants control the default message format (:data:`log_message_format`),
date format (:data:`log_date_format`), and the ordered list of log levels used
by the verbosity mapper (:data:`log_levels`).
"""

import logging

__all__ = [
    "logging",
    "log_message_format",
    "log_date_format",
    "log_levels",
    "get_verbosity",
    "set_log_level",
    "get_log_level",
    "setup_logger",
]

# log_message_format = "%(asctime)s %(levelname)s %(message)s"
log_message_format = "%(message)s"
"""Format string passed to :class:`logging.Formatter`.

Only the bare message is included by default (no timestamp or level prefix),
keeping CLI output clean.  The commented-out alternative above adds a
timestamp and level name.
"""
log_date_format = "%Y-%m-%d %H:%M:%S"
"""``datefmt`` string used when :data:`log_message_format` includes
``%(asctime)s``."""
log_levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
"""Ordered sequence of :mod:`logging` level constants, from least to most verbose.

Index 0 -> :data:`logging.ERROR` (default, ``-v`` count = 0),
index 1 -> :data:`logging.WARNING`,
index 2 -> :data:`logging.INFO`,
index 3 -> :data:`logging.DEBUG`.
Used by :func:`get_verbosity` to translate a verbosity count to a level.
"""


def get_verbosity(verbose: int) -> int:
    """Map a verbosity count to a :mod:`logging` level integer.

    The mapping follows the order of :data:`log_levels`
    ``[ERROR, WARNING, INFO, DEBUG]``, capped at ``DEBUG`` regardless of
    how large ``verbose`` is.

    Args:
        verbose (int): Number of ``-v`` flags provided by the caller.
            ``0`` -> ``ERROR``, ``1`` -> ``WARNING``, ``2`` -> ``INFO``,
            ``3+`` -> ``DEBUG``.

    Returns:
        int: A :mod:`logging` level constant (e.g. :data:`logging.DEBUG`).
    """
    # Define log level based on verbosity count
    log_level = int(
        log_levels[
            min(verbose, len(log_levels) - 1)
        ]  # Max verbosity is DEBUG (3)
    )
    # Set log level
    return log_level


def set_log_level(logger: logging.Logger, log_level: int) -> None:
    """Set the log level on a logger instance.

    Args:
        logger (logging.Logger): The logger to configure.
        log_level (int): A :mod:`logging` level constant
            (e.g. :data:`logging.DEBUG`, :data:`logging.INFO`).
    """
    # Set log level
    logger.setLevel(log_level)


def get_log_level(logger: logging.Logger) -> int:
    """Get the effective log level of a logger instance.

    Args:
        logger (logging.Logger): The logger to inspect.

    Returns:
        int: The effective :mod:`logging` level (walks up the logger
        hierarchy via :meth:`~logging.Logger.getEffectiveLevel` if no
        level is explicitly set on ``logger``).
    """
    log_level = logger.getEffectiveLevel()
    # level_str = logging.getLevelName(log_level)
    return log_level


def setup_logger(verbose: int) -> logging.Logger:
    """Create or retrieve the package logger and configure it for the given verbosity.

    Fetches the logger for this module via :func:`logging.getLogger`, attaches
    a :class:`~logging.StreamHandler` with :data:`log_message_format` /
    :data:`log_date_format` formatting if no handlers are already present
    (prevents duplicate handlers on repeated calls), then sets the level using
    :func:`get_verbosity`.

    Args:
        verbose (int): Number of ``-v`` flags (verbosity count).  Passed
            directly to :func:`get_verbosity` to resolve the logging level.

    Returns:
        logging.Logger: The configured logger instance.

    Example:
        >>> import logging
        >>> from valkyrie_tools.logger import setup_logger
        >>> logger = setup_logger(0)
        >>> logger.level == logging.ERROR
        True
        >>> logger = setup_logger(2)
        >>> logger.level == logging.INFO
        True
    """
    logger = logging.getLogger(__name__)
    # Check if a StreamHandler already exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        # get basename of script and name is filename
        # without extension
        formatter = logging.Formatter(log_message_format, log_date_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Set log level
    set_log_level(logger, get_verbosity(verbose))
    return logger
