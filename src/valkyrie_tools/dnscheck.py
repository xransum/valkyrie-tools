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
    """Print the results of the DNS query."""
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
    """Check whois on domains and ip addresses."""
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
