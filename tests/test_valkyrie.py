"""Valkyrie command tests."""
import unittest

from click.testing import CliRunner

from valkyrie_tools.valkyrie import cli


class TestWhobe(unittest.TestCase):
    """Test suite for whobe command."""

    def setUp(self) -> None:
        """Set up test fixtures, if any."""
        self.runner = CliRunner()

    def tearDown(self) -> CliRunner:
        """Tear down test fixtures, if any."""
        self.runner = None

    def test_version_option(self) -> None:
        """Test --version option."""
        result = self.runner.invoke(cli, ["--version"])
        name, version = result.output.split(" ")

        # Check name is correct
        self.assertEqual(name, "valkyrie")
        # Check version is a valid semantic version scheme
        for v in version.strip().split("."):
            self.assertTrue(v.isdigit())

        # Check clean exit
        self.assertEqual(result.exit_code, 0)

    def test_help_option(self) -> None:
        """Test --help option."""
        result = self.runner.invoke(cli, ["--help"])
        self.assertIn("Show version and exit.", result.output)
        self.assertEqual(result.exit_code, 0)

    def test_empty_args(self) -> None:
        """It exits with a status code of 0."""
        result = self.runner.invoke(cli, [])
        self.assertEqual(result.exit_code, 0)
