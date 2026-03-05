"""Command-line script for checking IP address information.

Queries ipinfo.io for geolocation and ASN metadata for one or more public IPv4
or IPv6 addresses.  Private addresses are detected locally and skipped without
making a network request.
"""

import sys
from typing import Tuple

import click

from .commons import common_options, extract_ip_addrs, parse_input_methods
from .constants import HELP_SHORT_TEXT, NO_ARGS_TEXT
from .ipaddr import get_ip_info, is_private_ip


PRIVATE_IP_SKIP_MESSAGE = "Skipped, private ip address."
"""Message printed when an IP address falls within
:data:`~valkyrie_tools.ipaddr.PRIVATE_IP_CIDR_RANGES`.
"""


@common_options(
    cmd_type=click.command,
    name="ipcheck",
    description="Get ip address info.",
    version="0.1.0",
)
@click.pass_context
def cli(
    ctx: click.Context,
    values: Tuple[str, ...],
    interactive: bool,
) -> None:
    """Look up geolocation and ASN metadata for IP addresses.

    Accepts one or more IPv4 or IPv6 addresses as positional arguments (or via
    stdin / interactive mode).  For each address:

    * Private addresses (per :data:`~valkyrie_tools.ipaddr.PRIVATE_IP_CIDR_RANGES`)
      are skipped with a notice.
    * Public addresses are queried against the ipinfo.io JSON API and the
      returned key/value pairs are printed in aligned columns.

    Args:
        ctx (click.Context): Click context object (injected by
            :func:`click.pass_context`).
        values (Tuple[str, ...]): Positional IP address arguments provided
            on the command line.
        interactive (bool): When ``True``, reads IP addresses from stdin
            in interactive mode.
    """
    values = parse_input_methods(values, interactive, ctx)
    if len(values) == 0:
        click.echo("Error: %s" % NO_ARGS_TEXT, err=True)
        click.echo(HELP_SHORT_TEXT.format(name=ctx.command.name), err=True)
        sys.exit(1)
    args = extract_ip_addrs("\n".join(values), unique=True)

    for a in range(len(args)):
        ipaddr = args[a]
        click.echo(f"> {ipaddr}".format(ipaddr))

        if is_private_ip(ipaddr):
            click.echo("  %s" % PRIVATE_IP_SKIP_MESSAGE)
            continue

        ipinfo = get_ip_info(ipaddr)

        key_width = max([len(k) for k in ipinfo.keys()]) + 1

        for k, v in ipinfo.items():
            click.echo(f"  {k:<{key_width}}: {v}")

        # Print trailing newline
        if a < len(args) - 1:
            click.echo()
