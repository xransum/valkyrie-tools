"""Test suite for base command flags.

Inherited unittest class mixin imported from command test suites.
"""

from unittest.mock import patch

from click.testing import CliRunner

from valkyrie_tools.constants import (  # HELP_VERSION_TEXT,
    INTERACTIVE_MODE_PROMPT,
    NO_ARGS_TEXT,
)


class BaseCommandTest:
    """Base test case for commands with shared args and flags."""

    # Overridden in subclasses
    command = None

    def setUp(self) -> None:
        """Set up test fixtures, if any."""
        self.runner = CliRunner()

    def tearDown(self) -> CliRunner:
        """Tear down test fixtures, if any."""
        self.runner = None

    def test_help_option(self) -> None:
        """Test --help flag."""
        result = self.runner.invoke(self.command, ["--help"])
        # self.assertIn("Show version and exit.", result.output)
        self.assertIn("Usage: ", result.output)
        self.assertEqual(result.exit_code, 0)

    def test_interactive_mode(self) -> None:
        """Test --interactive flag."""
        # Mock the sys.stdin read method to simulate user input.
        with patch("valkyrie_tools.commons.sys") as mock_sys:
            # Override isatty to simulate a terminal and simulate
            # user input.
            mock_sys.stdin.isatty.return_value = True
            mock_sys.stdin.read.side_effect = [
                " ",  # Empty value
                "",  # Simulates CTRL+d
            ]

            result = self.runner.invoke(self.command, ["--interactive"])

        self.assertIn(INTERACTIVE_MODE_PROMPT, result.output)
        self.assertEqual(result.exit_code, 1)

    def test_empty_args(self) -> None:
        """Test empty args for exit code of 1."""
        result = self.runner.invoke(self.command, [])
        self.assertIn(NO_ARGS_TEXT, result.output)
        self.assertEqual(result.exit_code, 1)
