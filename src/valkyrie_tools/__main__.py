"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Valkyrie Tools."""


if __name__ == "__main__":
    main(prog_name="valkyrie")  # pragma: no cover
