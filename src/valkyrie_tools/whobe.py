"""Whobe command-line script."""
import sys
from typing import Any, Dict, Optional, Tuple

import click

from .commons import (
    common_options,
    extract_domains,
    extract_ip_addrs,
    parse_input_methods,
)
from .constants import HELP_SHORT_TEXT, NO_ARGS_TEXT
from .ipaddr import get_net_size, is_valid_ip_addr
from .whois import get_ip_whois, get_whois


NO_WHOIS_MSG = "No whois data"


def print_ip_whois(whois: Optional[Dict[str, Any]]) -> None:  # pragma: no cover
    """Print results to the terminal."""
    if isinstance(whois, dict) is False:
        click.echo("No whois data.", err=True)
    else:
        click.echo(
            f'   ASN: {whois.get("asn", "Unknown")}'
            f' ({whois.get("asn_country_code", "Unknown")})'
        )
        click.echo("   CIDR: %s" % whois.get("asn_cidr", "Unknown"))
        click.echo("   Description: %s" % whois.get("asn_cidr", "Unknown"))
        click.echo("   Networks:")

        # Filter out networks that don't have a name or handle
        nets = filter(
            lambda x: isinstance(x, dict)
            and x.get("name") is not None
            and x.get("handle") is not None,
            whois.get("nets", []) or [],
        )
        for net in nets:
            # Print the network name and handle
            click.echo(f'      - {net.get("name", "Unknown")} ', nl=False)
            click.echo(f'({net.get("handle", "Unknown")})')

            # Print the netrange and total number of hosts
            click.echo(f'        CIDR: {net["cidr"]}')
            click.echo(f'        Netrange: ({net["range"]})', nl=False)
            click.echo(f' - {get_net_size(net["cidr"])} Hosts')

            # Print the address and location
            click.echo("        Address: ", nl=False)
            address = net.get("address", "Unknown")
            if isinstance(address, str) is True:
                address = address.replace("\n", " ").strip()

            click.echo(address, nl=False)
            city = net.get("city", "Unknown")
            if isinstance(city, str) is True:
                click.echo(f", {city}", nl=False)

            country = net.get("country", "Unknown")
            if isinstance(country, str) is True:
                click.echo(f", {country}", nl=False)

            postal_code = net.get("postal_code", "")
            if isinstance(postal_code, str) is True:
                click.echo(f" {postal_code}", nl=False)

            click.echo("")

            # Print the emails
            click.echo("        Emails: ", nl=False)
            if isinstance(net.get("emails", []), (list, tuple)) is True:
                click.echo("")
                for email in net["emails"]:
                    click.echo(f"          - {email}")
            else:
                click.echo(net.get("emails", "Unknown"))


def print_whois(whois: Optional[Dict[str, Any]]) -> None:  # pragma: no cover
    """Print results to the terminal."""
    if isinstance(whois, dict) is False:
        click.echo(NO_WHOIS_MSG, err=True)
    else:
        click.echo(
            f'   Registrar: {whois.get("registrar", "Unknown")} '
            f'({whois.get("org", "Unknown")})'
        )

        click.echo(f'   Status: {whois.get("status", "Unknown").split(" ")[0]}')

        click.echo("   Emails: ")
        emails = whois.get("emails", ["None"])
        if isinstance(emails, str):
            emails = [emails]

        for email in emails:
            click.echo(f"      - {email}")

        click.echo(f"   Name: {whois.get('name', 'Unknown')}")

        click.echo("   Address: ", nl=False)
        address = whois.get("address", "Unknown")
        city = whois.get("city", "Unknown")
        country = whois.get("country", "Unknown")
        state = whois.get("state", "Unknown")
        postal_code = whois.get("registrant_postal_code", "")
        click.echo(f"{address}, {city}, {state} {postal_code}, {country}")

        creation_date = whois.get("creation_date")
        click.echo(f"   Creation Date: {creation_date}")

        expiration_date = whois.get("expiration_date")
        click.echo(f"   Expiration Date: {expiration_date}")

        updated_date = whois.get("updated_date")
        click.echo(f"   Updated Date: {updated_date}")

        click.echo("   Name Servers: ")
        name_servers = whois.get("name_servers", ["None"])
        if isinstance(name_servers, (list, tuple)):
            for ns in whois["name_servers"]:
                click.echo(f"      - {ns}")
        else:
            click.echo(f"     - {name_servers}")


@common_options(
    name="whobe",
    description="Check whois on domains and ip addresses.",
    version="0.1.0",
)
@click.pass_context
def cli(
    ctx: click.Context,
    values: Tuple[str, ...],
    interactive: bool,
) -> None:
    """Check whois on domains and ip addresses."""
    values = parse_input_methods(values, interactive, ctx)
    if len(values) == 0:
        click.echo("Error: %s" % NO_ARGS_TEXT, err=True)
        click.echo(HELP_SHORT_TEXT.format(name=ctx.command.name), err=True)
        sys.exit(1)

    ip_addrs = extract_ip_addrs("\n".join(values), unique=True)
    domains = extract_domains("\n".join(values), unique=True)
    args = ip_addrs + domains

    for a in range(len(args)):
        arg = args[a]
        click.echo(f"> {arg}".format(arg))

        if is_valid_ip_addr(arg):
            whois = get_ip_whois(arg)
            print_ip_whois(whois)
        else:
            whois = get_whois(arg)
            print_whois(whois)

        # Print trailing newline
        if a < len(args) - 1:
            click.echo()


if __name__ == "__main__":  # pragma: no cover
    cli()
