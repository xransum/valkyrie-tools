"""Tests for dnscheck module."""
import unittest
from unittest.mock import patch

from valkyrie_tools.dnscheck import cli

from .test_base_command import BaseCommandTest


class TestDnscheck(BaseCommandTest, unittest.TestCase):
    """Test suite for dnscheck command."""

    command = cli

    def setUp(self):
        """Set up test fixtures, if any."""
        super().setUp()

    def tearDown(self):
        """Tear down test fixtures, if any."""
        super().tearDown()

    def test_successful(self):
        """Test for success."""
        # Mock the arguments
        mock_ip = "1.1.1.1"
        # Run the command
        result = self.runner.invoke(self.command, [mock_ip])
        # Assert the result
        self.assertIn(mock_ip, result.output)

    @patch("valkyrie_tools.dnscheck.get_dns_records")
    def test_multiple_ip(self, mock_get_dns_records):
        """Test for multiple ip addresses."""
        # Mock the responses
        mock_args = ["1.1.1.1"]
        mock_results = [("PTR", "example.com")]
        mock_get_dns_records.side_effect = [mock_results]
        # Run the command
        std = self.runner.invoke(self.command, mock_args)
        # Assert the result
        for mock_arg in mock_args:
            self.assertIn(mock_arg, std.output)

        for rtype, resolve in mock_results:
            self.assertIn(rtype, std.output)
            self.assertIn(resolve, std.output)