"""Test suite for ipcheck command."""
import unittest
from unittest.mock import patch

from valkyrie_tools.ipcheck import PRIVATE_IP_SKIP_MESSAGE, cli

from .test_base_command import BaseCommandTest


class TestIpcheck(BaseCommandTest, unittest.TestCase):
    """Test suite for ipcheck command."""

    command = cli

    def setUp(self):
        """Set up test fixtures, if any."""
        # Call the setUp of the base class
        super().setUp()
        pass

    def tearDown(self):
        """Tear down test fixtures, if any."""
        # Call the tearDown of the base class
        super().tearDown()
        pass

    def test_successful(self):
        """Test for success."""
        # Mock the arguments
        mock_ip = "1.1.1.1"
        # Run the command
        result = self.runner.invoke(self.command, [mock_ip])
        # Assert the result
        self.assertIn(mock_ip, result.output)

    def test_private_ip_error(self):
        """Test for private ip."""
        # Mock the arguments
        mock_ip = "192.168.1.1"
        # Run the command
        result = self.runner.invoke(self.command, [mock_ip])
        # Assert the result
        self.assertIn(PRIVATE_IP_SKIP_MESSAGE, result.output)

    @patch("valkyrie_tools.ipcheck.get_ip_info")
    def test_multiple_ip(self, mock_get_ip_info):
        """Test for multiple ip addresses."""
        # Mock the responses
        mock_result = {
            "12.23.45.78": {"foo": "bar"},
            "98.76.54.32": {"baz": "qux"},
        }
        mock_ips = list(mock_result.keys())
        mock_get_ip_info.side_effect = lambda ip: mock_result[ip]
        # Run the command
        result = self.runner.invoke(self.command, mock_ips)

        # Assert the result
        for ip in mock_ips:
            for key, value in mock_result[ip].items():
                self.assertIn(key, result.output)
                self.assertIn(value, result.output)
