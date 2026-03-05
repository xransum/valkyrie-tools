"""Command-line script for checking url aliveness and status."""

import re
import sys
from typing import Any, Dict, Tuple, Union, cast

import click
import requests
from requests import Response

from .commons import common_options, extract_urls, parse_input_methods
from .constants import (  # URL_REGEX,
    DEFAULT_CATEGORIZED_HEADERS,
    HELP_SHORT_TEXT,
    NO_ARGS_TEXT,
)
from .exceptions import (
    REQUESTS_CONNECTION_ERROR_MESSAGES,
    REQUESTS_SSL_ERROR_MESSAGE,
    REQUESTS_TIMEOUT_ERROR_MESSAGE,
    REQUESTS_TOO_MANY_REDIRECTS_ERROR_MESSAGE,
    REQUESTS_UNHANDLED_CONNECTION_ERROR_MESSAGE,
)
from .httpr import build_redirect_chain, filter_headers, get_http_version_text


# Initialize global variables
HEADER_KEY_TRUNC_LENGTH = 70
"""Maximum character length for header values before they are truncated.

When ``--no-truncate`` is **not** passed, any header value longer than this
many characters is truncated to ``value[:HEADER_KEY_TRUNC_LENGTH] + "..."``.
"""
QUIET_MODE = False
"""Reserved flag for quiet output mode.  Currently unused by :func:`cli`."""
OUTPUT_FILE = None
"""Reserved variable for a future output-file option.  Currently unused by
:func:`cli`.
"""


@common_options(
    cmd_type=click.command,
    name="urlcheck",
    description="Check url(s) for their aliveness and status.",
    version="0.1.0",
)
@click.option(
    "-t",
    "--no-truncate",
    "no_truncate",
    is_flag=True,
    help="Disable header truncation.",
    default=False,
)
@click.option(
    "-S",
    "--show-headers",
    "show_headers",
    is_flag=True,
    help="Disable header truncation.",
    default=False,
)
@click.pass_context
def cli(  # noqa: C901
    ctx: click.Context,
    values: Tuple[str, ...],
    interactive: bool,
    no_truncate: bool,
    show_headers: bool,
) -> None:
    """Check URL(s) for aliveness, HTTP status, and redirect chains.

    Accepts one or more URLs as positional arguments (or via stdin / interactive
    mode) and follows each URL's full redirect chain, printing the HTTP version,
    status code, reason, and a filtered set of response headers for every hop.

    Use ``-S`` / ``--show-headers`` to display all response headers instead of
    the default curated set.  Use ``-t`` / ``--no-truncate`` to prevent long
    header values from being truncated to
    :data:`~valkyrie_tools.urlcheck.HEADER_KEY_TRUNC_LENGTH` characters.

    Args:
        ctx (click.Context): Click context object (injected by
            :func:`click.pass_context`).
        values (Tuple[str, ...]): Positional URL arguments provided on the
            command line.
        interactive (bool): When ``True``, reads URLs from stdin in
            interactive mode.
        no_truncate (bool): When ``True``, disables truncation of long
            header values.
        show_headers (bool): When ``True``, displays all response headers
            instead of only the curated CDN/proxy subset.
    """
    args = parse_input_methods(values, interactive, ctx)

    if len(args) == 0:
        click.echo("Error: %s" % NO_ARGS_TEXT, err=True)
        click.echo(HELP_SHORT_TEXT.format(name=ctx.command.name), err=True)
        sys.exit(1)

    urls = []
    for arg in args:
        for url in extract_urls(arg):
            if url not in urls:
                urls.append(url)

    for u in range(len(urls)):
        url = urls[u]
        results = build_redirect_chain("GET", url, 30, {}, None, True)

        for r in range(len(results)):
            hop = results[r]  # type: Any
            hop_url = cast(str, hop[0])
            response = cast(Union[Response, Exception, None], hop[1])

            padding = 3
            # Print the URL
            if r <= 0:
                click.echo("->", nl=False)
            else:
                padding = 3
                click.echo(">>", nl=False)

            click.echo(" ", nl=False)
            click.echo(hop_url, nl=False)
            click.echo()

            if isinstance(response, Exception):
                click.echo(" " * padding, nl=False, err=True)

                if isinstance(response, requests.exceptions.SSLError):
                    click.echo(REQUESTS_SSL_ERROR_MESSAGE, err=True)
                elif isinstance(response, requests.exceptions.Timeout):
                    click.echo(REQUESTS_TIMEOUT_ERROR_MESSAGE, err=True)
                elif isinstance(response, requests.exceptions.TooManyRedirects):
                    click.echo(
                        REQUESTS_TOO_MANY_REDIRECTS_ERROR_MESSAGE, err=True
                    )
                elif isinstance(response, requests.exceptions.ConnectionError):
                    for (
                        search_text,
                        error_message,
                    ) in REQUESTS_CONNECTION_ERROR_MESSAGES.items():
                        if re.search(search_text, str(response)) is not None:
                            click.echo(error_message, err=True)
                            break

                    else:
                        click.echo(
                            REQUESTS_UNHANDLED_CONNECTION_ERROR_MESSAGE,
                            err=True,
                        )
                else:
                    click.echo(str(response), err=True)

                continue
            elif isinstance(response, Response):
                # Print the response status
                http_version = get_http_version_text(response.raw.version)
                status_code = response.status_code
                reason = response.reason

                click.echo(" " * padding, nl=False)
                click.echo("%s - %i - " % (http_version, status_code), nl=False)
                if 100 <= status_code < 200:
                    click.echo(reason)
                elif 200 <= status_code < 300:
                    click.echo(reason)
                elif 300 <= status_code < 400:
                    click.echo(reason)
                elif 400 <= status_code < 500:
                    click.echo(reason)
                else:
                    click.echo(reason)

                # Print the response headers
                resp_headers = cast(Dict[str, str], dict(response.headers))
                if show_headers is True:
                    resp_headers = filter_headers(resp_headers, [])
                else:
                    resp_headers = filter_headers(
                        resp_headers,
                        [
                            v
                            for vv in DEFAULT_CATEGORIZED_HEADERS.values()
                            for v in vv
                        ],
                    )

                for key, val in resp_headers.items():
                    click.echo(" " * padding, nl=False)
                    click.echo(key, nl=False)
                    click.echo(": ", nl=False)
                    if (
                        len(val) > HEADER_KEY_TRUNC_LENGTH
                        and no_truncate is False
                    ):
                        val = val[:HEADER_KEY_TRUNC_LENGTH] + "..."

                    click.echo(val)

        # Add a newline between URLs, but not after the last one
        if u < len(urls) - 1:
            click.echo("")


if __name__ == "__main__":  # pragma: no cover
    cli()
