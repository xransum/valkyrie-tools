"""Valkyrie command tests."""

import os
import unittest
from unittest.mock import patch

from appdirs import user_config_dir
from click.testing import CliRunner

from valkyrie_tools import __appname__
from valkyrie_tools.config import Config
from valkyrie_tools.valkyrie import cli


test_config_file = f"test_{__appname__}"
test_config_file_path = os.path.join(user_config_dir(), f".{test_config_file}")
test_config_defaults = {
    "GLOBAL": {"testKey": "testValue"},
}


class TestValkyrie(unittest.TestCase):
    """Test suite for whobe command."""

    command = cli

    def setUp(self) -> None:
        """Set up test fixtures, if any."""
        self.runner = CliRunner()
        self.test_config = Config(
            test_config_file, defaults=test_config_defaults
        )

    def tearDown(self) -> CliRunner:
        """Tear down test fixtures, if any."""
        self.runner = None
        if os.path.exists(test_config_file_path):
            # os.remove(test_config_file_path)
            pass

    def test_version_option(self) -> None:
        """Test --version option."""
        result = self.runner.invoke(self.command, ["--version"])
        name, _, version = result.output.split(" ")

        # Check name is correct
        self.assertEqual(name[:-1], "valkyrie")

        # Check version is a valid semantic version scheme
        for v in version.strip().split("."):
            self.assertTrue(v.isdigit())

        # Check clean exit
        self.assertEqual(result.exit_code, 0)

    # def test_help_option(self) -> None:
    #     """Test --help option."""
    #     result = self.runner.invoke(cli, ["--help"])
    #     self.assertIn("Show the version and exit.", result.output)
    #     self.assertEqual(result.exit_code, 0)

    @patch("valkyrie_tools.valkyrie.configs")
    def test_config_set(self, mock_configs) -> None:
        """Test set sub-command."""
        # Replace what is bound to the configs variable with our test config
        mock_configs.return_value = self.test_config

        result = self.runner.invoke(
            cli.commands["config"].commands["set"], ["setKey", "setValue"]
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Updated setKey.", result.output)

    @patch("valkyrie_tools.valkyrie.configs")
    def test_config_get(self, mock_configs) -> None:
        """Test get sub-command."""
        mock_configs.return_value = self.test_config
        mock_configs.get.return_value = "testValue"
        result = self.runner.invoke(
            cli.commands["config"].commands["get"], ["testKey"]
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("testKey: testValue", result.output)

    @patch("valkyrie_tools.valkyrie.configs")
    def test_config_delete(self, mock_configs) -> None:
        """Test delete sub-command."""
        mock_configs.return_value = self.test_config

        result = self.runner.invoke(
            cli.commands["config"].commands["delete"], ["testKey"]
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Deleted testKey.", result.output)

    @patch("valkyrie_tools.valkyrie.configs")
    @patch("click.echo")
    def test_config_list(self, mock_click_echo, mock_configs) -> None:
        """Test list sub-command."""
        mock_configs.return_value = self.test_config
        result = self.runner.invoke(cli.commands["config"].commands["list"], [])
        self.assertEqual(result.exit_code, 0)
        # mock_click_echo.assert_called()

    @patch("valkyrie_tools.valkyrie.configs")
    @patch("click.echo")
    def test_config_list_value(self, mock_click_echo, mock_configs) -> None:
        """Test list sub-command."""
        mock_configs.return_value = self.test_config
        result = self.runner.invoke(
            cli.commands["config"].commands["list"], ["testKey"]
        )
        self.assertEqual(result.exit_code, 0)
        # mock_click_echo.assert_called()

    @patch("valkyrie_tools.valkyrie.configs")
    @patch("click.echo")
    def test_config_list_value_uppercase(
        self, mock_click_echo, mock_configs
    ) -> None:
        """Test list sub-command."""
        mock_configs.return_value = self.test_config
        result = self.runner.invoke(
            cli.commands["config"].commands["list"], ["TESTKEY"]
        )
        self.assertEqual(result.exit_code, 0)
        # mock_click_echo.assert_called()
