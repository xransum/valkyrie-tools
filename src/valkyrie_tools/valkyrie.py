"""Command-line interface for Valkyrie Tools.

Entry point for the ``valkyrie`` command group, which exposes a ``config``
sub-group with ``set``, ``get``, ``delete``, and ``list`` sub-commands for
managing the user's persistent configuration file.
"""

from typing import Optional

import click

from . import __version__, configs
from .commons import emit_json


@click.group(
    help="Valkyrie Toolkit Interface.",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option(version=__version__, prog_name="valkyrie")
def cli() -> None:
    """Valkyrie Toolkit command group.

    Top-level entry point.  Use ``valkyrie config`` to manage the persistent
    configuration file (stored in the platform user-config directory).

    Sub-commands:

    * ``config set <key> <value>`` - write a configuration key
    * ``config get <key>`` - read a configuration key
    * ``config delete <key>`` - remove a configuration key
    * ``config list [key]`` - list all keys (or filter by name)
    """
    pass  # pragma: no cover


@cli.group(name="config")
def config_group() -> None:
    """Configuration management."""
    pass  # pragma: no cover


@config_group.command(name="set")
@click.option(
    "-j",
    "--json",
    "output_json",
    is_flag=True,
    help="Output result as JSON.",
    default=False,
)
@click.argument("key", metavar="key")
@click.argument("value", metavar="value")
def set_config(output_json: bool, key: str, value: str) -> None:
    """Set a configuration value.

    Args:
        output_json (bool): When ``True``, emits the result as a JSON object.
        key (str): Configuration key to set.
        value (str): Value to assign to ``key``.
    """
    configs.set("GLOBAL", key, value)
    if output_json:
        emit_json({"key": key, "updated": True})
        return
    click.echo(f"Updated {key}.")


@config_group.command(name="get")
@click.option(
    "-j",
    "--json",
    "output_json",
    is_flag=True,
    help="Output result as JSON.",
    default=False,
)
@click.argument("key", metavar="key")
def get_config(output_json: bool, key: str) -> None:
    """Get a configuration value.

    Args:
        output_json (bool): When ``True``, emits the result as a JSON object.
        key (str): Configuration key to retrieve.
    """
    value = configs.get("GLOBAL", key)
    if output_json:
        emit_json({"key": key, "value": value})
        return
    click.echo(f"{key}: {value}")


@config_group.command(name="delete")
@click.option(
    "-j",
    "--json",
    "output_json",
    is_flag=True,
    help="Output result as JSON.",
    default=False,
)
@click.argument("key", metavar="key")
def delete_config(output_json: bool, key: str) -> None:
    """Delete a configuration value.

    Args:
        output_json (bool): When ``True``, emits the result as a JSON object.
        key (str): Configuration key to delete.
    """
    configs.remove_option("GLOBAL", key)
    if output_json:
        emit_json({"key": key, "deleted": True})
        return
    click.echo(f"Config updated: {configs.config_file}")
    click.echo(f"Deleted {key}.")


@config_group.command(name="list")
@click.option(
    "-j",
    "--json",
    "output_json",
    is_flag=True,
    help="Output result as JSON.",
    default=False,
)
@click.argument("key", metavar="key", required=False)
def list_config(output_json: bool, key: Optional[str] = None) -> None:
    """List configuration values.

    Args:
        output_json (bool): When ``True``, emits the result as a JSON array.
        key (Optional[str]): Optional key name to filter by.
    """
    items = list(configs.config.items("GLOBAL"))

    if key is not None:
        items = [
            (k, v) for k, v in items if k.lower() == key.lower()
        ]  # pragma: no cover

    if output_json:
        emit_json([{"key": k, "value": v} for k, v in items])
        return

    for k, v in items:
        click.echo(f"{k}: {v}")  # pragma: no cover


if __name__ == "__main__":
    cli()  # pragma: no cover
