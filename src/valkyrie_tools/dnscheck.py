"""DNS lookup command-line script."""

import sys
from typing import List, Tuple

import click

from .commons import (
    common_options,
    extract_domains,
    extract_ip_addrs,
    parse_input_methods,
)
from .constants import HELP_SHORT_TEXT, NO_ARGS_TEXT
from .dns import DEFAULT_RECORD_TYPES, RECORD_TYPES, get_dns_records


def print_results(arg: str, results: dict) -> None:
    """Print formatted DNS query results to stdout.

    Displays the queried argument as a header line followed by each record
    type-value pair, aligned by the longest record type name in the result
    set.

    Args:
        arg (str): The domain or IP address that was queried.
        results (dict): An iterable of ``(record_type, value)`` tuples as
            returned by :func:`~valkyrie_tools.dns.get_dns_records`.
    """
    click.echo(f"> {arg}".format(arg))
    rtype_len = max([len(rtype) for rtype, _ in results])
    for key, value in results:
        click.echo(f"  {key:{rtype_len}}: {value}")


@common_options(
    cmd_type=click.command,
    name="dnscheck",
    description="Check DNS records for domains and IP addresses.",
    version="0.1.0",
)
@click.option(
    "-t",
    "--rtypes",
    "record_types",
    help="DNS record type to query.",
    type=click.Choice(RECORD_TYPES),
    multiple=True,
    default=DEFAULT_RECORD_TYPES,
)
@click.pass_context
def cli(
    ctx: click.Context,
    values: Tuple[str, ...],
    interactive: bool,
    record_types: List[str],
) -> None:  # noqa: C901
    """Check DNS records for domains and IP addresses.

    Accepts one or more domains or IP addresses as positional arguments (or via
    stdin / interactive mode) and prints all matching DNS records for each
    requested record type.

    Args:
        ctx (click.Context): Click context object (injected by
            :func:`click.pass_context`).
        values (Tuple[str, ...]): Positional domain or IP address arguments
            provided on the command line.
        interactive (bool): When ``True``, reads values from stdin in
            interactive mode.
        record_types (List[str]): DNS record types to query (e.g. ``"A"``,
            ``"MX"``).  Defaults to
            :data:`~valkyrie_tools.dns.DEFAULT_RECORD_TYPES`.
    """
    args = parse_input_methods(values, interactive, ctx)

    if len(args) == 0:
        click.echo("Error: %s" % NO_ARGS_TEXT, err=True)
        click.echo(HELP_SHORT_TEXT.format(name=ctx.command.name), err=True)
        sys.exit(1)

    ip_addrs = extract_ip_addrs("\n".join(values), unique=True)
    domains = extract_domains("\n".join(values), unique=True)
    args = list(set(ip_addrs + domains))

    for a in range(len(args)):
        arg = args[a]
        results = get_dns_records(arg, record_types=record_types)
        print_results(arg, results)

        # Print trailing newline
        if a < len(args) - 1:  # pragma: no cover
            click.echo()
