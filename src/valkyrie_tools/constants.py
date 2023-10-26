"""Constants modules"""



__all__ = [
    "HELP_SHORT_TEXT",
    "NO_ARGS_TEXT",
    "INVALID_ARG_TEXT",
    "INVALID_FLAG_TEXT",
    "BINARY_FILE_READ_ERROR",
    "YES_NO_PROMPT",
    "INTERACTIVE_MODE_PROMPT",
]

# Errors
HELP_SHORT_TEXT = "Try '%s --help' or '%s -h' for more information"
NO_ARGS_TEXT = "No arg(s) provided"
INVALID_ARG_TEXT = "Invalid %s"
INVALID_FLAG_TEXT = "Invalid flag %s"
BINARY_FILE_READ_ERROR = "Cannot read binary files"

# Prompts
YES_NO_PROMPT = "%s [y/N]: "
INTERACTIVE_MODE_PROMPT = "Enter the text (CTRL+d to finalize):"
