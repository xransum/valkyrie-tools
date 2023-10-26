"""Logger module."""
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
log_date_format = "%Y-%m-%d %H:%M:%S"
log_levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]


def get_verbosity(verbose: int) -> int:
    """Log level getter function."""
    # Define log level based on verbosity count
    log_level = int(
        log_levels[min(verbose, len(log_levels) - 1)]  # Max verbosity is DEBUG (3)
    )
    # Set log level
    return log_level


def set_log_level(logger: logging.Logger, log_level: int) -> None:
    """Log level setter function."""
    # Set log level
    logger.setLevel(log_level)


def get_log_level(logger: logging.Logger) -> int:
    """Log level getter function."""
    log_level = logger.getEffectiveLevel()
    # level_str = logging.getLevelName(log_level)
    return log_level


def setup_logger(verbose: int) -> logging.Logger:
    """Wrapper function with built-in verbosity handling."""
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
    set_log_level(logger, verbose)
    return logger
