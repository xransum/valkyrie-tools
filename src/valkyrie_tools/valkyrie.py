"""Command-line interface."""
import click

from . import __version__
from .commons import sys_exit

__all__ = ["__version__"]

__prog_name__ = "valkyrie"
__prog_desc__ = "Valkyrie tools cli interface."


# def deactivate_prompts(ctx, param, value):
#     if value:
#         for p in ctx.command.params:
#             if isinstance(p, click.Option) and p.prompt is not None:
#                 p.prompt = None
#     return value
#
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


@click.command(
    name=__prog_name__,
    help=__prog_desc__,
    context_settings=dict(help_option_names=["-h", "--help"]),
    hidden=True,
)
@click.version_option(
    __version__,
    "-V",
    "--version",
    message="%(prog)s %(version)s",
    help="Show version and exit.",
)
@click.pass_context
def cli(
    ctx: click.Context,  # noqa: C901
) -> None:
    """Entry point to the valkyrie-tools suite."""
    sys_exit("%s functionality not yet implemented", 1)


if __name__ == "__main__":
    cli()  # pragma: no cover
