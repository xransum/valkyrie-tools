"""Command-line script for checking url aliveness and status."""
import io
import re
import sys
from typing import Optional

import click
import requests

from .commons import URL_REGEX, read_value_from_input
from .constants import DEFAULT_CATEGORIZED_HEADERS
from .exceptions import (
    REQUESTS_CONNECTION_ERROR_MESSAGES,
    REQUESTS_SSL_ERROR_MESSAGE,
    REQUESTS_TIMEOUT_ERROR_MESSAGE,
    REQUESTS_TOO_MANY_REDIRECTS_ERROR_MESSAGE,
    REQUESTS_UNHANDLED_CONNECTION_ERROR_MESSAGE,
)
from .httpr import build_redirect_chain, filter_headers, get_http_version_text

__prog_name__ = "urlcheck"
__prog_desc__ = "Check url(s) for their aliveness and status."
__version__ = "0.1.0"

# Initialize global variables
HEADER_KEY_TRUNC_LENGTH = 70
QUIET_MODE = False
OUTPUT_FILE = None


@click.command(
    name=__prog_name__,
    help=__prog_desc__,
    context_settings=dict(help_option_names=["-h", "--help"]),
    hidden=True,
)
@click.option(
    "-o",
    "--output",
    "output",
    type=click.File("w", encoding="utf8"),
    help="Output file.",
    # default=click.get_text_stream("stdout"),
    default=None,
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
    "-I",
    "--show-headers",
    "show_headers",
    is_flag=True,
    help="Disable header truncation.",
    default=False,
)
@click.option(
    "-i", "--interactive", is_flag=True, help="Interactive mode.", default=False
)
@click.version_option(
    __version__,
    "-V",
    "--version",
    message="%(prog)s %(version)s",
    help="Show version and exit.",
)
@click.argument("values", nargs=-1, required=False)
# @click.pass_context
def cli(  # noqa: C901
    # ctx: click.Context,
    values: Optional[str],
    output: Optional[io.StringIO],
    interactive: bool,
    no_truncate: bool,
    show_headers: bool,
) -> None:
    """This is to test args and stdin."""
    global QUIET_MODE

    # Set global variables
    QUIET_MODE = False

    # Check if values is empty
    values = list(values)
    values = read_value_from_input(values, interactive, name=__prog_name__)
    # values = handle_value_argument(values, None)
    values = [v for v in values if v is not None and v != ""]
    if values is None or len(values) == 0:
        click.echo("Input args cannot be empty.", err=True)
        sys.exit(1)

    urls = []
    for value in values:
        for url in re.findall(URL_REGEX, value):
            if url not in urls:
                urls.append(url)

    for u in range(len(urls)):
        url = urls[u]
        results = build_redirect_chain("GET", url, 30, {}, None, True)

        for r in range(len(results)):
            url, response = results[r]

            padding = 3
            # Print the URL
            if r <= 0:
                click.echo("->", nl=False, file=output)
            else:
                padding = 3
                click.echo(">>", nl=False, file=output)

            click.echo(" ", nl=False, file=output)
            click.echo(url, nl=False, file=output)
            click.echo(file=output)

            if issubclass(type(response), Exception):
                click.echo(" " * padding, nl=False, err=True, file=output)

                if isinstance(response, requests.exceptions.SSLError):
                    click.echo(REQUESTS_SSL_ERROR_MESSAGE, err=True, file=output)
                elif isinstance(response, requests.exceptions.Timeout):
                    click.echo(REQUESTS_TIMEOUT_ERROR_MESSAGE, err=True, file=output)
                elif isinstance(response, requests.exceptions.TooManyRedirects):
                    click.echo(
                        REQUESTS_TOO_MANY_REDIRECTS_ERROR_MESSAGE,
                        err=True,
                        file=output,
                    )
                elif isinstance(response, requests.exceptions.ConnectionError):
                    for (
                        search_text,
                        error_message,
                    ) in REQUESTS_CONNECTION_ERROR_MESSAGES.items():
                        if re.search(search_text, str(response)) is not None:
                            click.echo(error_message, err=True, file=output)
                            break

                    else:
                        click.echo(
                            REQUESTS_UNHANDLED_CONNECTION_ERROR_MESSAGE,
                            err=True,
                            file=output,
                        )
                else:
                    click.echo(str(response), err=True, file=output)

                continue
            else:
                # Print the response status
                http_version = get_http_version_text(response.raw.version)
                status_code = response.status_code
                reason = response.reason

                click.echo(" " * padding, nl=False, file=output)
                click.echo(
                    "%s - %i - " % (http_version, status_code),
                    nl=False,
                    file=output,
                )
                if 100 <= status_code < 200:
                    click.echo(reason, file=output)
                elif 200 <= status_code < 300:
                    click.echo(reason, file=output)
                elif 300 <= status_code < 400:
                    click.echo(reason, file=output)
                elif 400 <= status_code < 500:
                    click.echo(reason, file=output)
                else:
                    click.echo(reason, file=output)

                # Print the response headers
                headers = response.headers
                if show_headers is True:
                    headers = filter_headers(response.headers, [])
                else:
                    headers = filter_headers(
                        response.headers,
                        [v for vv in DEFAULT_CATEGORIZED_HEADERS.values() for v in vv],
                    )

                for key, val in headers.items():
                    click.echo(" " * padding, nl=False, file=output)
                    click.echo(key, nl=False, file=output)
                    click.echo(": ", nl=False, file=output)
                    if len(val) > HEADER_KEY_TRUNC_LENGTH and no_truncate is False:
                        val = val[:HEADER_KEY_TRUNC_LENGTH] + "..."

                    click.echo(val, file=output)

        # Add a newline between URLs, but not after the last one
        if u < len(urls) - 1:
            click.echo("", file=output)


if __name__ == "__main__":  # pragma: no cover
    cli()
