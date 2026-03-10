"""Test suite for base command flags.

Inherited unittest class mixin imported from command test suites.
"""

import json
import unittest
from typing import Optional
from unittest.mock import patch

import click
from click.testing import CliRunner

from valkyrie_tools.constants import (  # HELP_VERSION_TEXT,
    INTERACTIVE_MODE_PROMPT,
    NO_ARGS_TEXT,
)


class BaseCommandTest(unittest.TestCase):
    """Base test case for commands with shared args and flags."""

    # Overridden in subclasses; typed Optional so mypy accepts the class-level
    # default while subclasses set it to a real click.BaseCommand.
    command: Optional[click.Command] = None

    def setUp(self) -> None:
        """Set up test fixtures, if any."""
        self.runner: CliRunner = CliRunner()

    def tearDown(self) -> None:
        """Tear down test fixtures, if any."""
        self.runner = CliRunner()  # reset to a fresh runner

    def test_help_option(self) -> None:
        """Test --help flag."""
        if self.command is None:
            self.skipTest("BaseCommandTest requires a subclass to set command")
        result = self.runner.invoke(self.command, ["--help"])
        # self.assertIn("Show version and exit.", result.output)
        self.assertIn("Usage: ", result.output)
        self.assertEqual(result.exit_code, 0)

    def test_interactive_mode(self) -> None:
        """Test --interactive flag."""
        if self.command is None:
            self.skipTest("BaseCommandTest requires a subclass to set command")
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
        if self.command is None:
            self.skipTest("BaseCommandTest requires a subclass to set command")
        result = self.runner.invoke(self.command, [])
        self.assertIn(NO_ARGS_TEXT, result.output)
        self.assertEqual(result.exit_code, 1)

    def test_json_flag_empty_args(self) -> None:
        """Test --json with no args emits empty array and exits 0."""
        if self.command is None:
            self.skipTest("BaseCommandTest requires a subclass to set command")
        result = self.runner.invoke(self.command, ["--json"])
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)
