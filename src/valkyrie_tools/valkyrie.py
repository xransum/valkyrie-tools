"""Command-line interface."""
import click

from . import __version__
from .logger import setup_logger

__all__ = ["__version__"]

logger = None

# def deactivate_prompts(ctx, param, value):
#     if value:
#         for p in ctx.command.params:
#             if isinstance(p, click.Option) and p.prompt is not None:
#                 p.prompt = None
#     return value


@click.command(
    name="valkyrie",
    help="Valkyrie tools cli interface.",
    context_settings=dict(help_option_names=["-h", "--help"]),
    hidden=True,
)
# @click.option(
#    "-s",
#    "--silent",
#    is_flag=True,
#    default=False,
#    is_eager=True,
#    expose_value=False,
#    callback=deactivate_prompts,
#    help="Silent mode",
# )
@click.option("-v", "--verbose", count=True, help="Make the operation more talkative")
@click.version_option(
    __version__,
    "-V",
    "--version",
    message="%(prog)s %(version)s",
    help="Show version number and quit",
)
def cli(
    verbose: int,
) -> None:
    """This script is the entry point to the valkyrie-tools cli."""
    global logger
    logger = setup_logger(verbose)
    logger.debug("Debug mode enabled")


if __name__ == "__main__":
    cli()  # pragma: no cover
