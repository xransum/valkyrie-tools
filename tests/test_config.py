"""Config module tests."""

import os
import unittest

from valkyrie_tools.config import Config


# configparser, os
# appdirs.user_config_dir


class TestConfig(unittest.TestCase):
    """Test case for the Config object."""

    def setUp(self) -> None:
        """Set up test fixtures, if any."""
        # we need to create a mock ConfigParser object
        self.mock_config_name = "test_config.ini"
        self.mock_defaults = {"test_section": {"test_key": "test_value"}}
        self.mock_config = Config(
            config_name=self.mock_config_name, defaults=self.mock_defaults
        )
        self.mock_config_file = self.mock_config.config_file

    def tearDown(self) -> None:
        """Tear down test fixtures, if any."""
        # Remove the mock config file and directory
        if os.path.exists(self.mock_config_file):
            os.remove(self.mock_config_file)

    def test_init(self) -> None:
        """Test the Config object initialization."""
        self.assertIsInstance(self.mock_config, Config)

    def test_defaults(self) -> None:
        """Test the defaults attribute."""
        self.assertEqual(self.mock_config.defaults, self.mock_defaults)

    def test_config_name(self) -> None:
        """Test the config_name attribute."""
        self.assertEqual(self.mock_config.config_name, self.mock_config_name)

    def test_config_file(self) -> None:
        """Test the config_file attribute."""
        self.assertEqual(self.mock_config.config_file, self.mock_config_file)

    def test_get(self) -> None:
        """Test the get method."""
        self.assertEqual(
            self.mock_config.get("test_section", "test_key"), "test_value"
        )

    def test_get_fallback(self) -> None:
        """Test the get method with a fallback value."""
        self.assertEqual(
            self.mock_config.get("test_section", "test_key", "fallback"),
            "test_value",
        )

    def test_set(self) -> None:
        """Test the set method."""
        self.mock_config.set("test_section", "test_key", "new_value")
        self.assertEqual(
            self.mock_config.get("test_section", "test_key"), "new_value"
        )

    def test_set_new_section(self) -> None:
        """Test the set method with a new section."""
        self.mock_config.set("new_section", "new_key", "new_value")
        self.assertEqual(
            self.mock_config.get("new_section", "new_key"), "new_value"
        )

    def test_remove_section(self) -> None:
        """Test the remove_section method."""
        self.mock_config.remove_section("test_section")
        self.assertIsNone(self.mock_config.get("test_section", "test_key"))

    def test_remove_option(self) -> None:
        """Test the remove_option method."""
        self.mock_config.remove_option("test_section", "test_key")
        self.assertIsNone(self.mock_config.get("test_section", "test_key"))

    def test_save(self) -> None:
        """Test the save method."""
        self.mock_config.save()
        self.assertTrue(os.path.exists(self.mock_config_file))

    def test_set_defaults(self) -> None:
        """Test the set_defaults method."""
        self.mock_defaults = {
            "new_section": {
                "new_key": "new_value",
            },
            "test_section": {
                "test_key": "test_value",
            },
        }
        self.mock_config.defaults = self.mock_defaults
        self.mock_config.set_defaults()
        self.assertEqual(
            self.mock_config.get("new_section", "new_key"), "new_value"
        )
        self.assertEqual(
            self.mock_config.get("test_section", "test_key"), "test_value"
        )
