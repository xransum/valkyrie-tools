"""Constants test module."""
from valkyrie_tools.constants import (
    BINARY_FILE_READ_ERROR,
    HELP_SHORT_TEXT,
    INTERACTIVE_MODE_PROMPT,
    INVALID_ARG_TEXT,
    INVALID_FLAG_TEXT,
    NO_ARGS_TEXT,
    YES_NO_PROMPT,
)


def test_help_short_text() -> None:
    """Tests the HELP_SHORT_TEXT constant."""
    assert HELP_SHORT_TEXT == "Try '%s --help' or '%s -h' for more information"


def test_no_args_text() -> None:
    """Tests the NO_ARGS_TEXT constant."""
    assert NO_ARGS_TEXT == "No arg(s) provided"


def test_invalid_arg_text() -> None:
    """Tests the INVALID_ARG_TEXT constant."""
    assert INVALID_ARG_TEXT == "Invalid %s"


def test_invalid_flag_text() -> None:
    """Tests the INVALID_FLAG_TEXT constant."""
    assert INVALID_FLAG_TEXT == "Invalid flag %s"


def test_binary_file_read_error() -> None:
    """Tests the BINARY_FILE_READ_ERROR constant."""
    assert BINARY_FILE_READ_ERROR == "Cannot read binary files"


def test_yes_no_prompt() -> None:
    """Tests the YES_NO_PROMPT constant."""
    assert YES_NO_PROMPT == "%s [y/N]: "


def test_interactive_mode_prompt() -> None:
    """Tests the INTERACTIVE_MODE_PROMPT constant."""
    assert INTERACTIVE_MODE_PROMPT == "Enter the text (CTRL+d to finalize):"
