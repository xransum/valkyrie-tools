"""Command-line interface."""
from typing import Any, Dict, List

import click

from . import __version__
from .commons import common_options


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


@common_options(
    name="valkyrie",
    description="Valkyrie tools cli interface.",
    version=__version__,
)
@click.pass_context
def cli(
    ctx: click.Context,  # noqa: B008
    *args: List[Any],  # noqa: B008
    **kwargs: Dict[str, Any],  # noqa: B008
) -> None:
    """Entry point to the valkyrie-tools suite."""
    pass


if __name__ == "__main__":
    cli()  # pragma: no cover
