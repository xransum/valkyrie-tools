"""Command-line interface for Valkyrie Tools.

Entry point for the ``valkyrie`` command group, which exposes a ``config``
sub-group with ``set``, ``get``, ``delete``, and ``list`` sub-commands for
managing the user's persistent configuration file, and a ``virustotal``
sub-group for querying the VirusTotal API.
"""

from typing import Optional

import click

from . import __version__, configs
from .virustotal import cli as virustotal_group


# @common_options(
#    cmd_type=click.group,
#    name="valkyrie",
#    description="Vallyrie Tools Toolkit Interface.",
#    version=__version__,
# )
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
    * ``virustotal`` - VirusTotal threat intelligence sub-commands
    """
    pass  # pragma: no cover


cli.add_command(virustotal_group)


@cli.group(name="config")
def config_group() -> None:
    """Configuration management."""
    pass  # pragma: no cover


@config_group.command(name="set")
@click.argument("key", metavar="key")
@click.argument("value", metavar="value")
def set_config(key: str, value: str) -> None:
    """Set a configuration value."""
    configs.set("GLOBAL", key, value)
    # click.echo(f"Config updated: {configs.config_file}")
    # click.echo(f"Config updated: {configs.config_file}")
    click.echo(f"Updated {key}.")


@config_group.command(name="get")
@click.argument("key", metavar="key")
def get_config(key: str) -> None:
    """Get a configuration value."""
    value = configs.get("GLOBAL", key)
    click.echo(f"{key}: {value}")


@config_group.command(name="delete")
@click.argument("key", metavar="key")
def delete_config(key: str) -> None:
    """Delete a configuration value."""
    configs.remove_option("GLOBAL", key)
    click.echo(f"Config updated: {configs.config_file}")
    click.echo(f"Deleted {key}.")


@config_group.command(name="list")
@click.argument("key", metavar="key", required=False)
def list_config(key: Optional[str] = None) -> None:
    """List configuration values."""
    if key is not None:
        for key, value in configs.config.items("GLOBAL"):
            if key.lower() == key.lower():  # pragma: no cover
                click.echo(f"{key}: {value}")
    else:
        for key, value in configs.config.items("GLOBAL"):
            click.echo(f"{key}: {value}")  # pragma: no cover


if __name__ == "__main__":
    cli()  # pragma: no cover
