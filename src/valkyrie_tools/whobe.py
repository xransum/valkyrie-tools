"""Whobe command-line script."""

import sys
from typing import Any, Dict, List, Optional, Tuple

import click

from .commons import (
    common_options,
    emit_json,
    extract_domains,
    extract_ip_addrs,
    parse_input_methods,
)
from .constants import HELP_SHORT_TEXT, NO_ARGS_TEXT
from .ipaddr import get_net_size, is_valid_ip_addr
from .whois import get_ip_whois, get_whois


NO_WHOIS_MSG = "No whois data"
"""Message printed to stderr when :func:`get_whois` returns
``None``.
"""  # pragma: no cover


def json_extractor_whobe(data: List[Any]) -> Tuple[str, ...]:
    """Extract target domains/IPs from upstream valkyrie-tools JSON.

    Accepts any array of objects that each contain an ``"input"`` key, which
    is the shape produced by every valkyrie-tools command.

    Args:
        data (List[Any]): Decoded JSON array from stdin.

    Returns:
        Tuple[str, ...]: Tuple of ``input`` values to query.

    Raises:
        ValueError: If ``data`` does not match a recognised upstream schema.
    """
    if all(isinstance(entry, dict) and "input" in entry for entry in data):
        return tuple(str(entry["input"]) for entry in data)

    raise ValueError(
        "Unrecognised upstream JSON schema for whobe. "
        "Expected a valkyrie-tools --json output array "
        "(objects with an 'input' key)."
    )


def ip_whois_to_dict(
    arg: str, whois: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Convert IP WHOIS data to a JSON-serialisable dict.

    Args:
        arg (str): The IP address that was queried.
        whois (Optional[Dict[str, Any]]): Parsed IP WHOIS record, or
            ``None``.

    Returns:
        Dict[str, Any]: Dict with ``"input"``, ``"type"``, and WHOIS fields,
        or an ``"error"`` key when ``whois`` is not a dict.
    """
    if not isinstance(whois, dict):
        return {"input": arg, "type": "ip", "error": "No whois data."}

    nets: List[Dict[str, Any]] = []
    raw_nets = filter(
        lambda x: (
            isinstance(x, dict)
            and x.get("name") is not None
            and x.get("handle") is not None
        ),
        whois.get("nets", []) or [],
    )
    for net in raw_nets:
        net_entry: Dict[str, Any] = {
            "name": net.get("name"),
            "handle": net.get("handle"),
            "cidr": net.get("cidr"),
            "range": net.get("range"),
            "address": net.get("address"),
            "city": net.get("city"),
            "country": net.get("country"),
            "postal_code": net.get("postal_code"),
            "emails": net.get("emails") or [],
            "hosts": get_net_size(net["cidr"]) if net.get("cidr") else None,
        }
        nets.append(net_entry)

    return {
        "input": arg,
        "type": "ip",
        "asn": whois.get("asn"),
        "asn_country_code": whois.get("asn_country_code"),
        "asn_cidr": whois.get("asn_cidr"),
        "nets": nets,
    }


def domain_whois_to_dict(
    arg: str, whois: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Convert domain WHOIS data to a JSON-serialisable dict.

    Args:
        arg (str): The domain that was queried.
        whois (Optional[Dict[str, Any]]): Parsed domain WHOIS record, or
            ``None``.

    Returns:
        Dict[str, Any]: Dict with ``"input"``, ``"type"``, and WHOIS fields,
        or an ``"error"`` key when ``whois`` is not a dict.
    """
    if not isinstance(whois, dict):
        return {"input": arg, "type": "domain", "error": NO_WHOIS_MSG}

    emails = whois.get("emails", [])
    if isinstance(emails, str):
        emails = [emails]

    name_servers = whois.get("name_servers", [])
    if isinstance(name_servers, str):
        name_servers = [name_servers]

    return {
        "input": arg,
        "type": "domain",
        "registrar": whois.get("registrar"),
        "org": whois.get("org"),
        "emails": emails,
        "name": whois.get("name"),
        "address": whois.get("address"),
        "city": whois.get("city"),
        "state": whois.get("state"),
        "country": whois.get("country"),
        "registrant_postal_code": whois.get("registrant_postal_code"),
        "creation_date": whois.get("creation_date"),
        "expiration_date": whois.get("expiration_date"),
        "updated_date": whois.get("updated_date"),
        "name_servers": list(name_servers) if name_servers else [],
    }


def print_ip_whois(whois: Optional[Dict[str, Any]]) -> None:  # pragma: no cover
    """Print IP WHOIS data to the terminal.

    Expects the dict returned by :func:`~valkyrie_tools.whois.get_ip_whois`
    (i.e. ``IPWhois.lookup_whois()`` output).  Relevant top-level keys:

    * ``asn`` - ASN number string (e.g. ``"15169"``)
    * ``asn_country_code`` - two-letter country code
    * ``asn_cidr`` - CIDR block announced by the ASN
    * ``nets`` - list of network dicts, each with:
      ``name``, ``handle``, ``cidr``, ``range``, ``address``, ``city``,
      ``country``, ``postal_code``, ``emails``

    If ``whois`` is not a :class:`dict`, an error message is printed to
    stderr instead.

    Args:
        whois (Optional[Dict[str, Any]]): Parsed IP WHOIS record, or ``None``.
    """
    if not isinstance(whois, dict):
        click.echo("No whois data.", err=True)
    else:
        click.echo(
            f"   ASN: {whois.get('asn', 'Unknown')}"
            f" ({whois.get('asn_country_code', 'Unknown')})"
        )
        click.echo("   CIDR: %s" % whois.get("asn_cidr", "Unknown"))
        click.echo("   Description: %s" % whois.get("asn_cidr", "Unknown"))
        click.echo("   Networks:")

        # Filter out networks that don't have a name or handle
        nets = filter(
            lambda x: (
                isinstance(x, dict)
                and x.get("name") is not None
                and x.get("handle") is not None
            ),
            whois.get("nets", []) or [],
        )
        for net in nets:
            # Print the network name and handle
            click.echo(f"      - {net.get('name', 'Unknown')} ", nl=False)
            click.echo(f"({net.get('handle', 'Unknown')})")

            # Print the netrange and total number of hosts
            click.echo(f"        CIDR: {net['cidr']}")
            click.echo(f"        Netrange: ({net['range']})", nl=False)
            click.echo(f" - {get_net_size(net['cidr'])} Hosts")

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
    """Print domain WHOIS data to the terminal.

    Expects the dict returned by :func:`~valkyrie_tools.whois.get_whois`
    (i.e. a :class:`whois.parser.WhoisEntry` / :class:`whois.parser.WhoisCom`
    object, which behaves like a dict).  Keys consumed:

    * ``registrar`` - registrar name
    * ``org`` - registrant organisation
    * ``emails`` - str or list of contact e-mail addresses
    * ``name`` - registrant name
    * ``address``, ``city``, ``state``, ``country``,
      ``registrant_postal_code`` - registrant address fields
    * ``creation_date``, ``expiration_date``, ``updated_date`` - lifecycle dates
    * ``name_servers`` - list (or str) of authoritative name servers

    If ``whois`` is not a :class:`dict`, :data:`NO_WHOIS_MSG` is printed to
    stderr instead.

    Args:
        whois (Optional[Dict[str, Any]]): Parsed domain WHOIS record, or
            ``None``.
    """
    if not isinstance(whois, dict):
        click.echo(NO_WHOIS_MSG, err=True)
    else:
        click.echo(
            f"   Registrar: {whois.get('registrar', 'Unknown')} "
            f"({whois.get('org', 'Unknown')})"
        )

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
            for ns in name_servers:
                click.echo(f"      - {ns}")
        else:
            click.echo(f"     - {name_servers}")


@common_options(
    cmd_type=click.command,
    name="whobe",
    description="Check whois on domains and ip addresses.",
    version="0.1.0",
)
@click.pass_context
def cli(
    ctx: click.Context,
    values: Tuple[str, ...],
    interactive: bool,
    output_json: bool,
) -> None:
    """Check whois on domains and ip addresses.

    Accepts one or more domains or IP addresses as positional arguments (or
    via stdin / interactive mode).

    When ``--json`` is active, results are emitted as a JSON array.  Each
    entry has ``"input"`` and ``"type"`` keys plus the relevant WHOIS fields,
    or an ``"error"`` key when no data is available.

    Args:
        ctx (click.Context): Click context object (injected by
            :func:`click.pass_context`).
        values (Tuple[str, ...]): Positional domain or IP address arguments
            provided on the command line.
        interactive (bool): When ``True``, reads values from stdin in
            interactive mode.
        output_json (bool): When ``True``, emits results as a JSON array
            instead of human-readable text.
    """
    values = parse_input_methods(
        values,
        interactive,
        ctx,
        output_json=output_json,
        json_extractor=json_extractor_whobe,
    )
    if len(values) == 0:
        if output_json:
            emit_json([])
            sys.exit(0)
        click.echo("Error: %s" % NO_ARGS_TEXT, err=True)
        click.echo(HELP_SHORT_TEXT.format(name=ctx.command.name), err=True)
        sys.exit(1)

    ip_addrs = extract_ip_addrs("\n".join(values), unique=True)
    domains = extract_domains("\n".join(values), unique=True)
    args = ip_addrs + domains

    if output_json:
        json_results: List[Dict[str, Any]] = []
        for arg in args:
            if is_valid_ip_addr(arg):
                whois: Any = get_ip_whois(arg)
                json_results.append(ip_whois_to_dict(arg, whois))
            else:
                domain_whois: Any = get_whois(arg)
                json_results.append(domain_whois_to_dict(arg, domain_whois))
        emit_json(json_results)
        return

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
