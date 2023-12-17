"""Logger test module."""
from valkyrie_tools.logger import (
    get_log_level,
    get_verbosity,
    log_levels,
    set_log_level,
    setup_logger,
)


logger = setup_logger(0)


def test_get_verbosity() -> None:
    """Sets the verbosity level for a level."""
    for level in range(len(log_levels)):
        set_log_level(logger, level)
        assert get_verbosity(level) == log_levels[level]


def test_get_verbosity_out_of_range() -> None:
    """Sets the verbosity level for a level."""
    # Last value should be DEBUG
    levels_count = len(log_levels)
    set_log_level(logger, get_verbosity(levels_count - 1))
    assert int(get_log_level(logger)) == int(log_levels[levels_count - 1])


def test_get_log_level() -> None:
    """Sets the verbosity level for a level."""
    for level in range(len(log_levels)):
        set_log_level(logger, get_verbosity(level))
        assert get_log_level(logger) is not None


def test_get_log_level_out_of_range() -> None:
    """Sets the verbosity level for a level."""
    # Last value should be DEBUG
    levels_count = len(log_levels)
    set_log_level(logger, levels_count - 1)
    assert int(get_verbosity(len(log_levels) - 1)) == int(
        log_levels[levels_count - 1]
    )


def test_setup_logger() -> None:
    """Sets the verbosity level for a level."""
    for level in range(len(log_levels)):
        set_log_level(logger, level)
        assert setup_logger(level) is not None
