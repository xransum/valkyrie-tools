"""Valkyrie test module."""
import pytest
from _pytest.logging import LogCaptureFixture
from click.testing import CliRunner

from valkyrie_tools.valkyrie import __version__, cli  # deactivate_prompts,


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_version_option(runner: CliRunner) -> None:
    """Test --version option."""
    result = runner.invoke(cli, ["-V"])
    assert result.exit_code == 0
    # assert 3 == len(result.output.strip().split("."))
    assert __version__ in result.output


def test_verbose_option(runner: CliRunner, caplog: LogCaptureFixture) -> None:
    """Test --verbose option."""
    result = runner.invoke(cli, ["-v"])
    assert result.exit_code == 0
    assert "Debug mode enabled" in caplog.text


def test_cli_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(cli)
    assert result.exit_code == 0


# def test_deactivate_prompts() -> None:
#     """Test deactivate_prompts function"""
#     ctx = click.Context(cli)
#     deactivate_prompts(ctx, None, True)
#     for p in ctx.command.params:
#         if isinstance(p, click.Option) and p.prompt is not None:
#             assert p.prompt is None
