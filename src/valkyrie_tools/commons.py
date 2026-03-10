"""Shared utilities for valkyrie-tools CLI commands.

Provides the :func:`common_options` Click decorator (which wires up
``--interactive``, ``--json``, and a variadic ``values`` argument for every
command), input-handling helpers (:func:`parse_input_methods`,
:func:`handle_file_input`, :func:`parse_json_stdin`, :func:`emit_json`),
and a family of regex-based extraction functions for domains, IP addresses,
e-mail addresses, and URLs.
"""

from __future__ import annotations

import json
import os
import re
import sys
from functools import wraps
from typing import Any, Callable, List, Optional, Tuple, Union  # noqa: F401

import click
from art import text2art  # type: ignore[import-untyped]  # no stubs available

from .constants import (
    DOMAIN_REGEX,
    EMAIL_ADDR_REGEX,
    INTERACTIVE_MODE_PROMPT,
    IPV4_REGEX,
    IPV6_REGEX,
    URL_REGEX,
)
from .files import is_binary_file

__all__ = [
    "common_options",
    "emit_json",
    "parse_json_stdin",
    "print_version",
    "parse_input_methods",
    "extract_domains",
    "extract_ipv4_addrs",
    "extract_ipv6_addrs",
    "extract_ip_addrs",
    "extract_emails",
    "extract_urls",
]


def common_options(
    cmd_type: Callable[..., Callable[[Any], Any]] = click.command,
    name: str = "",
    description: str = "",
    version: str = "",
) -> Callable[[Any], Any]:
    """Decorator to add common options to command-line tools.

    Allows for built-in command definitions and the flags:
    -h, --help: Show help message and exit.
    -V, --version: Show version and exit.
    -vvv, --verbose: Enable verbose mode.
    -i, --interactive: Enable interactive mode.

    Args:
        cmd_type (Callable): Click command decorator factory (e.g. click.command).
        name (str): Name of the command.
        description (str): Description of the command.
        version (str): Version of the command in semantic versioning scheme.

    Returns:
        Callable: Decorator that wraps the command function.
    """

    def decorator(
        func: Any,
    ) -> Any:
        """Bind options to the command function."""

        @cmd_type(
            name=name,
            help=description,
            context_settings=dict(help_option_names=["-h", "--help"]),
            hidden=True,
        )
        @click.option(
            "-j",
            "--json",
            "output_json",
            is_flag=True,
            help="Output results as JSON.",
            default=False,
        )
        @click.option(
            "-I",
            "--interactive",
            is_flag=True,
            help="Interactive mode.",
            default=False,
        )
        @click.argument(
            "values", nargs=-1, type=click.UNPROCESSED, required=False
        )
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Ensure decorated function's metadata is preserved."""
            return func(*args, **kwargs)

        return wrapper

    return decorator


def print_version(version: str) -> Callable[..., None]:
    """Print version and exit.

    Args:
        version (str): Version of the command in semantic versioning scheme.

    Returns:
        Callable: Click callback function.

    Raises:
        TypeError: If ``version`` is an empty string.
    """
    if not version:
        raise TypeError("version must be a non-empty string")

    def echo_version(
        ctx: click.Context,
        param: click.Option | click.Parameter,  # noqa: B008
        value: str,
    ) -> None:
        """Print version and exit.

        Args:
            ctx (click.Context): Click context.
            param (Union[click.Option, click.Parameter]): Click option or
                parameter.
            value (str): Value of the option or parameter.
        """
        if not value or ctx.resilient_parsing:
            return

        click.echo(version)
        ctx.exit()

    return echo_version


def emit_json(data: list[Any] | Any) -> None:
    """Serialise ``data`` to JSON and print it to stdout.

    Uses ``default=str`` so that non-serialisable values (e.g.
    :class:`datetime.datetime` objects from WHOIS results) are coerced to
    their string representation rather than raising a :class:`TypeError`.

    Args:
        data (Union[List[Any], Any]): JSON-serialisable value (typically a
            list of dicts for tool commands, or a plain dict for single-item
            config sub-commands) to serialise and print.
    """
    click.echo(json.dumps(data, indent=2, default=str))


def parse_json_stdin(
    raw: str,
    extractor: Callable[[list[Any]], tuple[str, ...]],
) -> tuple[str, ...]:
    """Parse a JSON array from stdin and extract values using ``extractor``.

    Attempts to decode ``raw`` as a JSON array.  If decoding fails, or the
    result is not a list, a :class:`click.UsageError` is raised.  The
    decoded list is then passed to ``extractor``, which is a per-command
    function that inspects the JSON shape and returns the string values the
    command should process.

    Args:
        raw (str): Raw stdin text that should be a JSON array.
        extractor (Callable[[List[Any]], Tuple[str, ...]]): Per-command
            function that maps the decoded JSON array to a tuple of string
            targets.

    Returns:
        Tuple[str, ...]: Extracted string values for the command to process.

    Raises:
        UsageError: If ``raw`` is not valid JSON, not a JSON array, or
            ``extractor`` raises a :class:`ValueError` for an unrecognised
            upstream schema.
    """
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise click.UsageError(
            "Piped input is not valid JSON. Use --json on the upstream command."
        ) from exc

    if not isinstance(data, list):
        raise click.UsageError(
            "Piped JSON input must be a JSON array produced by another "
            "valkyrie-tools command."
        )

    try:
        return extractor(data)
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc


def handle_file_input(
    file_path: str,
) -> str | None:
    """Read a text file from the filesystem and return its contents.

    Performs safety checks before reading: binary files and directories are
    rejected with an :class:`OSError`.  Only plain text files (as detected by
    :func:`~valkyrie_tools.files.is_binary_file`) are read and returned.

    Args:
        file_path (str): Path to the file to read.

    Returns:
        Optional[str]: The stripped text content of the file, or ``None`` if
        the path is not a regular file (e.g. a missing path that somehow
        passes the directory check).

    Raises:
        OSError: If ``file_path`` is a binary file.
        OSError: If ``file_path`` is a directory.
    """
    value = None

    # Safely avoid binary files.
    if is_binary_file(file_path) is True:
        raise OSError("Binary file provided, not a text file.")
    # Avoid directories.
    elif os.path.isdir(file_path) is True:
        raise OSError("Directory provided, not a file.")

    # Handle as normal file.
    elif os.path.isfile(file_path) is True:
        # Read the file, if possible.
        with open(file_path, encoding="utf-8") as file:
            value = file.read().strip()

    return value


def parse_input_methods(
    values: tuple[str, ...],
    interactive: bool,
    ctx: click.Context,
    output_json: bool = False,
    json_extractor: Callable[[list[Any]], tuple[str, ...]] | None = None,
) -> tuple[str, ...]:
    """Parse input methods.

    This function will attempt to read from stdin if there's no values
    provided.  If there's a ``"-"`` in the values, it will also read from
    stdin.  If values are provided, it will attempt to read from the file
    path provided in the values.  If there's no file at the path provided,
    it will just use the value provided.

    When ``output_json`` is ``True`` and data is piped on stdin, the raw
    stdin text is treated as a JSON array produced by another
    valkyrie-tools command.  ``json_extractor`` is called to map the decoded
    array to a tuple of string targets; if ``json_extractor`` is ``None`` the
    raw text falls through to normal processing.

    Args:
        values (Tuple[str, ...]): Positional arguments.
        interactive (bool): Whether to enable interactive mode.
        ctx (click.Context): Click context.
        output_json (bool): Whether JSON output mode is active.
            Defaults to ``False``.
        json_extractor (Optional[Callable]): Per-command function that maps a
            decoded JSON array to a tuple of string targets.  Only used when
            ``output_json`` is ``True`` and stdin is not a TTY.
            Defaults to ``None``.

    Returns:
        Tuple[str, ...]: Tuple of arguments.
    """
    args: tuple[str, ...] = ()

    # When interactive is enabled, drop to an input stream.
    if interactive is True:
        # Convert the script name to ascii art as a header and print it.
        click.echo(text2art(ctx.command.name))

        # Print the interactive prompt and read from stdin.
        click.echo(INTERACTIVE_MODE_PROMPT)
        stdin = sys.stdin.read().strip()

        # Only add the users input if it isn't empty.
        if stdin != "":
            values += (stdin,)

    # Check if data is being piped
    elif sys.stdin.isatty() is False:
        # Check if there's a "-" in the values
        if "-" in values:
            # Before reading from stdin, need to remove the
            # "-" from the values.
            values = tuple(v for v in values if v != "-")

        # Read data from pipe
        piped = sys.stdin.read().strip()

        # In JSON mode with a registered extractor, treat piped input as a
        # JSON array from an upstream valkyrie-tools command.  Only attempt
        # parsing when there is actually content to parse; an empty pipe is
        # treated the same as no arguments.
        if output_json and json_extractor is not None and piped != "":
            return parse_json_stdin(piped, json_extractor)

        values += (piped,)

    # Iterate over each argument
    for arg in values:
        # Avoid empty strings since Path.exists return True for them.
        if os.path.exists(arg) is True:
            file_content = handle_file_input(arg)
            if file_content is None:  # pragma: no cover
                continue

            args += (file_content,)

        # Otherwise, tack on the arg to the tuple.
        else:
            args += (arg,)

    # Remove empty strings from args
    args = tuple(a for a in args if a != "")
    return args


# Regex extract functions
def _extract_regex(
    regex: re.Pattern[str], text: str, key: str | None, unique: bool = False
) -> list[str]:
    """Extract regex matches from text.

    Args:
        regex (re.Pattern): Regex pattern to use.
        text (str): Text to extract regex matches from.
        key (str, optional): Key to extract from regex match.
            Defaults to None.
        unique (bool): Whether to return unique matches only.
            Defaults to False.

    Returns:
        List[str]: List of matches.
    """
    matches = []
    for text_match in regex.finditer(text):
        match = text_match.group(key) if key else text_match.group()
        if unique and match in matches:
            continue

        matches.append(match)

    return matches


def extract_domains(text: str, unique: bool = False) -> list[str]:
    """Extract domains from text.

    Args:
        text (str): Text to extract domains from.
        unique (bool): Whether to return unique domains only.
            Defaults to False.

    Returns:
        List[str]: List of domains.
    """
    return _extract_regex(DOMAIN_REGEX, text, "domain", unique)


def extract_ipv4_addrs(text: str, unique: bool = False) -> list[str]:
    """Extract IPv4 addresses from text.

    Args:
        text (str): Text to extract IPv4 addresses from.
        unique (bool): Whether to return unique IPv4 addresses only.
            Defaults to False.

    Returns:
        List[str]: List of IPv4 addresses.
    """
    return _extract_regex(IPV4_REGEX, text, "ipv4", unique)


def extract_ipv6_addrs(text: str, unique: bool = False) -> list[str]:
    """Extract IPv6 addresses from text.

    Args:
        text (str): Text to extract IPv6 addresses from.
        unique (bool): Whether to return unique IPv6 addresses only.
            Defaults to False.

    Returns:
        List[str]: List of IPv6 addresses.
    """
    return _extract_regex(IPV6_REGEX, text, "ipv6", unique)


def extract_ip_addrs(text: str, unique: bool = False) -> list[str]:
    """Extract IPv4 and IPv6 addresses from text.

    Args:
        text (str): Text to extract IPv4 and IPv6 addresses from.
        unique (bool): Whether to return unique IPv4 and IPv6
            addresses only. Defaults to False.

    Returns:
        List[str]: List of IPv4 and IPv6 addresses.
    """
    return extract_ipv4_addrs(text, unique) + extract_ipv6_addrs(text, unique)


def extract_emails(text: str, unique: bool = False) -> list[str]:
    """Extract email addresses from text.

    Args:
        text (str): Text to extract email addresses from.
        unique (bool): Whether to return unique email addresses only.
            Defaults to False.

    Returns:
        List[str]: List of email addresses.
    """
    return _extract_regex(EMAIL_ADDR_REGEX, text, "email", unique)


def extract_urls(text: str, unique: bool = False) -> list[str]:
    """Extract URLs from text.

    Args:
        text (str): Text to extract URLs from.
        unique (bool): Whether to return unique URLs only. Defaults to False.

    Returns:
        List[str]: List of URLs.
    """
    return _extract_regex(URL_REGEX, text, "url", unique)
