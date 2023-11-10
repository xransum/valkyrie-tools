"""Package commons for valkyrie-tools."""
import os
import re
import sys
from typing import List, Optional, Union

import click
from art import text2art

from .constants import INTERACTIVE_MODE_PROMPT
from .files import read_file

__all__ = [
    "URL_REGEX",
    "DOMAIN_REGEX",
    "EMAIL_ADDR_REGEX",
    "IPV4_ADDR_REGEX",
    "IPV6_ADDR_REGEX",
    "sys_exit",
    "handle_value_argument",
    "read_value_from_input",
]

URL_REGEX = re.compile(
    r"(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|"
    + r"[-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[A-Z0-9+&@#"
    + r"\/%=~_|$])",
    re.I | re.M,
)
DOMAIN_REGEX = re.compile(
    r"((((?!-))[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63})\b", re.I | re.M
)
EMAIL_ADDR_REGEX = re.compile(
    r"([a-zA-Z0-9._-]+@((((?!-))[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}))",
    re.I | re.M,
)
IPV4_ADDR_REGEX = re.compile(
    r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?"
    + r"[0-9][0-9]?)",
    re.I | re.M,
)
IPV6_ADDR_REGEX = re.compile(
    r"(?<![:.\w])(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}(?![:.\w])", re.I | re.M
)


def sys_exit(text: str, code: int = 1, help_short: bool = False) -> None:
    """Exit with error.

    Args:
        text (str): Error message.
        code (int): Exit code. Defaults to 1.
        help_short (bool): Whether to show the short
            help message. Defaults to False.
    """
    click.echo(text, err=True)
    if help_short:
        click.echo("Try '--help' for more information", err=True)

    sys.exit(code)


def handle_value_argument(
    value: Union[str, List[str]], input_file: Optional[str]
) -> Union[str, List[str]]:
    """Handle the 'value' argument.

    If an input file is passed, then ignore the value. If no input
    file is given, check if the value is a file or a list of files,
    if not return value(s) as is.

    Args:
        value (Union[str, List[str]]): Value passed from the command line.
        input_file (Optional[str]): Input file.

    Returns:
        Union[str, List[str]]: Value(s) to process.
    """
    # If an input file is provided, read and return its content
    if input_file is not None:
        return read_file(input_file)

    # If value is a string, check if it's a file path
    if isinstance(value, str):
        if os.path.exists(value):
            return read_file(value)
        else:
            return value

    # If value is a list, iterate over its elements
    elif isinstance(value, list):
        values = []
        for v in value:
            if os.path.exists(v):
                values.append(read_file(v))
            else:
                values.append(v)
        return values

    # If value is neither a string nor a list, return it as is
    else:
        return value


def read_value_from_input(
    values: Optional[Union[str, List[str]]],
    interactive: bool = False,
    name: Optional[str] = None,
) -> List[Union[str, None]]:
    """Read text from input, handling interactive mode and piped input.

    Args:
        values (Optional[Union[str, List[str]]]): String or list of strings.
        interactive (bool): Enable interactive mode. Defaults to False.
        name (Optional[str], optional): Name of the tool. Defaults to None.

    Returns:
        List[Union[str, None]]: List of strings.
    """
    # If values is None, set it to empty list
    if values is None:
        values = []

    # If values is not list or tuple, convert it to list
    if isinstance(values, (list, tuple)) is False:
        values = [values]

    # Do nothing when values are passed
    if len(values) == 0:
        # Command called non-interactively
        if sys.stdin.isatty() is False:
            stdin = sys.stdin.read()
        else:
            if interactive:
                if name is not None:
                    click.echo(text2art(name))

                click.echo("Interactive mode: ENABLED\n")
                click.echo(INTERACTIVE_MODE_PROMPT)
                stdin = sys.stdin.read()
            else:
                stdin = None

        if stdin is not None:
            values = [stdin.strip()]
        else:
            values = []

    return values
