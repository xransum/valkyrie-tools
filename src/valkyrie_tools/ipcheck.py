"""Command-line script for checking IP address information.

Queries ipinfo.io for geolocation and ASN metadata for one or more public IPv4
or IPv6 addresses.  Private addresses are detected locally and skipped without
making a network request.
"""

import sys
from typing import Any, Dict, List, Tuple

import click

from .commons import (
    common_options,
    emit_json,
    extract_ip_addrs,
    parse_input_methods,
)
from .constants import HELP_SHORT_TEXT, NO_ARGS_TEXT
from .ipaddr import get_ip_info, is_private_ip

PRIVATE_IP_SKIP_MESSAGE = "Skipped, private ip address."
"""Message printed when an IP address falls within
:data:`~valkyrie_tools.ipaddr.PRIVATE_IP_CIDR_RANGES`.
"""  # pragma: no cover


def _build_ip_json_entry(ipaddr: str) -> Dict[str, Any]:
    """Build a single JSON result entry for one IP address.

    Args:
        ipaddr (str): The IP address to look up.

    Returns:
        Dict[str, Any]: A dict with an ``"input"`` key and either full
        ipinfo data or an ``"error"`` key.
    """
    if is_private_ip(ipaddr):
        return {"input": ipaddr, "error": PRIVATE_IP_SKIP_MESSAGE}

    ipinfo = get_ip_info(ipaddr)
    if ipinfo is None:
        return {"input": ipaddr, "error": "No data returned."}

    entry: Dict[str, Any] = {"input": ipaddr}
    entry.update(ipinfo)
    return entry


def _print_ip_text(ipaddr: str) -> None:
    """Print human-readable ipinfo output for one IP address.

    Args:
        ipaddr (str): The IP address to look up and print.
    """
    click.echo(f"> {ipaddr}".format(ipaddr))

    if is_private_ip(ipaddr):
        click.echo("  %s" % PRIVATE_IP_SKIP_MESSAGE)
        return

    ipinfo = get_ip_info(ipaddr)
    if ipinfo is None:
        return

    key_width = max([len(k) for k in ipinfo.keys()]) + 1
    for k, v in ipinfo.items():
        click.echo(f"  {k:<{key_width}}: {v}")


def json_extractor_ipcheck(data: List[Any]) -> Tuple[str, ...]:
    """Extract IP addresses from upstream JSON produced by dnscheck.

    Recognises the ``dnscheck`` output schema (array of objects each
    containing a ``"records"`` key with ``"A"`` and/or ``"AAAA"`` sub-keys)
    and returns all resolved IP values for ``ipcheck`` to process.

    Args:
        data (List[Any]): Decoded JSON array from stdin.

    Returns:
        Tuple[str, ...]: Flat tuple of IPv4/IPv6 address strings.

    Raises:
        ValueError: If ``data`` does not match a recognised upstream schema.
    """
    # Detect dnscheck output: list of objects with a "records" key.
    if all(isinstance(entry, dict) and "records" in entry for entry in data):
        ips: List[str] = []
        for entry in data:
            records = entry.get("records", {})
            for rtype in ("A", "AAAA"):
                for ip in records.get(rtype, []):
                    if ip not in ips:
                        ips.append(ip)
        return tuple(ips)

    raise ValueError(
        "Unrecognised upstream JSON schema for ipcheck. "
        "Expected dnscheck --json output (objects with a 'records' key)."
    )


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
    output_json: bool,
) -> None:
    """Look up geolocation and ASN metadata for IP addresses.

    Accepts one or more IPv4 or IPv6 addresses as positional arguments (or via
    stdin / interactive mode).  For each address:

    * Private addresses (per :data:`~valkyrie_tools.ipaddr.PRIVATE_IP_CIDR_RANGES`)
      are skipped with a notice.
    * Public addresses are queried against the ipinfo.io JSON API and the
      returned key/value pairs are printed in aligned columns.

    When ``--json`` is active, results are emitted as a JSON array.  Each
    entry contains either the full ipinfo dict (plus an ``"input"`` key) or
    an ``"error"`` key for addresses that could not be resolved.  Piped JSON
    from ``dnscheck --json`` is automatically parsed to extract ``A`` /
    ``AAAA`` record values.

    Args:
        ctx (click.Context): Click context object (injected by
            :func:`click.pass_context`).
        values (Tuple[str, ...]): Positional IP address arguments provided
            on the command line.
        interactive (bool): When ``True``, reads IP addresses from stdin
            in interactive mode.
        output_json (bool): When ``True``, emits results as a JSON array
            instead of human-readable text.
    """
    values = parse_input_methods(
        values,
        interactive,
        ctx,
        output_json=output_json,
        json_extractor=json_extractor_ipcheck,
    )

    if len(values) == 0:
        if output_json:
            emit_json([])
            sys.exit(0)
        click.echo("Error: %s" % NO_ARGS_TEXT, err=True)
        click.echo(HELP_SHORT_TEXT.format(name=ctx.command.name), err=True)
        sys.exit(1)

    args = extract_ip_addrs("\n".join(values), unique=True)

    if output_json:
        results: List[Dict[str, Any]] = [
            _build_ip_json_entry(ipaddr) for ipaddr in args
        ]
        emit_json(results)
        return

    for a in range(len(args)):
        _print_ip_text(args[a])

        # Print trailing newline
        if a < len(args) - 1:
            click.echo()


if __name__ == "__main__":  # pragma: no cover
    cli()
