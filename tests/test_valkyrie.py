"""Valkyrie command tests."""
import unittest

import pytest
from click.testing import CliRunner

from valkyrie_tools.valkyrie import __prog_desc__, __prog_name__, __version__, cli


class TestValkyrie(unittest.TestCase):
    """Test suite for the valkyrie_tools.valkyrie command."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Init test case object."""
        self.runner = CliRunner()
        self.cli = cli

    def test_version_option(self) -> None:
        """Test --version option."""
        result = self.runner.invoke(self.cli, ["--version"])
        assert __prog_name__ in result.output
        assert __version__ in result.output
        assert result.exit_code == 0

    def test_help_option(self) -> None:
        """Test --help option."""
        result = self.runner.invoke(self.cli, ["--help"])
        assert __prog_desc__ in result.output
        assert result.exit_code == 0

    def test_cli_empty_args(self) -> None:
        """It exits with a status code of 1."""
        result = self.runner.invoke(self.cli)
        assert result.exit_code == 1
