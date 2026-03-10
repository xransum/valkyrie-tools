"""DNS lookup command-line script."""

import sys
from typing import Any, Dict, List, Tuple

import click

from .commons import (
    common_options,
    emit_json,
    extract_domains,
    extract_ip_addrs,
    parse_input_methods,
)
from .constants import HELP_SHORT_TEXT, NO_ARGS_TEXT
from .dns import DEFAULT_RECORD_TYPES, RECORD_TYPES, get_dns_records


def json_extractor_dnscheck(data: List[Any]) -> Tuple[str, ...]:
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
        "Unrecognised upstream JSON schema for dnscheck. "
        "Expected a valkyrie-tools --json output array "
        "(objects with an 'input' key)."
    )


def print_results(arg: str, results: List[Tuple[str, str]]) -> None:
    """Print formatted DNS query results to stdout.

    Displays the queried argument as a header line followed by each record
    type-value pair, aligned by the longest record type name in the result
    set.

    Args:
        arg (str): The domain or IP address that was queried.
        results (List[Tuple[str, str]]): An iterable of
            ``(record_type, value)`` tuples as returned by
            :func:`~valkyrie_tools.dns.get_dns_records`.
    """
    click.echo(f"> {arg}".format(arg))
    rtype_len = max([len(rtype) for rtype, _ in results])
    for key, value in results:
        click.echo(f"  {key:{rtype_len}}: {value}")


def build_dns_result(
    arg: str, results: List[Tuple[str, str]]
) -> Dict[str, Any]:
    """Build a JSON-serialisable dict from DNS query results.

    Groups ``(record_type, value)`` tuples by record type so that each type
    maps to a list of values, e.g. ``{"A": ["1.2.3.4"], "MX": [...]}``.

    Args:
        arg (str): The domain or IP address that was queried.
        results (List[Tuple[str, str]]): Flat list of
            ``(record_type, value)`` tuples.

    Returns:
        Dict[str, Any]: Dict with ``"input"`` and ``"records"`` keys.
    """
    records: Dict[str, List[str]] = {}
    for rtype, value in results:
        records.setdefault(rtype, []).append(value)
    return {"input": arg, "records": records}


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
    output_json: bool,
    record_types: List[str],
) -> None:  # noqa: C901
    """Check DNS records for domains and IP addresses.

    Accepts one or more domains or IP addresses as positional arguments (or via
    stdin / interactive mode) and prints all matching DNS records for each
    requested record type.

    When ``--json`` is active, results are emitted as a JSON array where each
    entry has an ``"input"`` key and a ``"records"`` dict mapping record types
    to lists of values.

    Args:
        ctx (click.Context): Click context object (injected by
            :func:`click.pass_context`).
        values (Tuple[str, ...]): Positional domain or IP address arguments
            provided on the command line.
        interactive (bool): When ``True``, reads values from stdin in
            interactive mode.
        output_json (bool): When ``True``, emits results as a JSON array
            instead of human-readable text.
        record_types (List[str]): DNS record types to query (e.g. ``"A"``,
            ``"MX"``).  Defaults to
            :data:`~valkyrie_tools.dns.DEFAULT_RECORD_TYPES`.
    """
    args = parse_input_methods(
        values,
        interactive,
        ctx,
        output_json=output_json,
        json_extractor=json_extractor_dnscheck,
    )

    if len(args) == 0:
        if output_json:
            emit_json([])
            sys.exit(0)
        click.echo("Error: %s" % NO_ARGS_TEXT, err=True)
        click.echo(HELP_SHORT_TEXT.format(name=ctx.command.name), err=True)
        sys.exit(1)

    ip_addrs = extract_ip_addrs("\n".join(args), unique=True)
    domains = extract_domains("\n".join(args), unique=True)
    targets = list(set(ip_addrs + domains))  # type: List[str]

    if output_json:
        json_results: List[Dict[str, Any]] = []
        for arg in targets:
            dns_records = get_dns_records(arg, record_types=record_types)
            json_results.append(build_dns_result(arg, dns_records))
        emit_json(json_results)
        return

    for a in range(len(targets)):
        arg = targets[a]
        results = get_dns_records(arg, record_types=record_types)
        print_results(arg, results)

        # Print trailing newline
        if a < len(targets) - 1:  # pragma: no cover
            click.echo()


if __name__ == "__main__":  # pragma: no cover
    cli()
