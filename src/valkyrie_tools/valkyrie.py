"""Command-line interface."""
from typing import Optional

import click

from . import __version__, configs
from .commons import common_options


#@common_options(
#    cmd_type=click.group,
#    name="valkyrie",
#    description="Vallyrie Tools Toolkit Interface.",
#    version=__version__,
#)
@click.group(help='Valkyrie Toolkit Interface.', context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(version=__version__, prog_name='valkyrie')
def cli() -> None:
    """Valkyrie command."""
    pass


@cli.group(name="config")
def config_group() -> None:
    """Configuration management."""
    pass


@config_group.command(name="set")
@click.argument("key", metavar="key")
@click.argument("value", metavar="value")
def set_config(key: str, value: str) -> None:
    """Set a configuration value."""
    configs.set("GLOBAL", key, value)
    #click.echo(f"Config updated: {configs.config_file}")
    #click.echo(f"Config updated: {configs.config_file}")
    click.echo(f"Set {key} to {value}.")


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
def list_config(key: Optional[str]) -> None:
    """List configuration values."""
    if key:
        for key, value in configs.config.items("GLOBAL"):
            if key.lower() == key.lower():
                click.echo(f"{key}: {value}")
    else:
        for key, value in configs.config.items("GLOBAL"):
            click.echo(f"{key}: {value}")


if __name__ == "__main__":
    cli()  # pragma: no cover
