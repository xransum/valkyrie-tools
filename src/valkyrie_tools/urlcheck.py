"""Command-line script for checking url aliveness and status."""
import re
import sys
from typing import Tuple

import click
import requests

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
QUIET_MODE = False
OUTPUT_FILE = None


@common_options(
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
    """Check whois on domains and ip addresses."""
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
            url, response = results[r]

            padding = 3
            # Print the URL
            if r <= 0:
                click.echo("->", nl=False)
            else:
                padding = 3
                click.echo(">>", nl=False)

            click.echo(" ", nl=False)
            click.echo(url, nl=False)
            click.echo()

            if issubclass(type(response), Exception):
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
            else:
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
                headers = response.headers
                if show_headers is True:
                    headers = filter_headers(response.headers, [])
                else:
                    headers = filter_headers(
                        response.headers,
                        [
                            v
                            for vv in DEFAULT_CATEGORIZED_HEADERS.values()
                            for v in vv
                        ],
                    )

                for key, val in headers.items():
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
