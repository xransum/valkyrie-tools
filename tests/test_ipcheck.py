"""Test suite for ipcheck command."""

import json
import unittest
from unittest.mock import MagicMock, patch

from valkyrie_tools.ipcheck import (
    PRIVATE_IP_SKIP_MESSAGE,
    cli,
    json_extractor_ipcheck,
)

from .test_base_command import BaseCommandTest


class TestIpcheck(BaseCommandTest, unittest.TestCase):
    """Test suite for ipcheck command."""

    command = cli

    def setUp(self) -> None:
        """Set up test fixtures, if any."""
        # Call the setUp of the base class
        super().setUp()
        pass

    def tearDown(self) -> None:
        """Tear down test fixtures, if any."""
        # Call the tearDown of the base class
        super().tearDown()
        pass

    def test_successful(self) -> None:
        """Test for success."""
        # Mock the arguments
        mock_ip = "1.1.1.1"
        # Run the command
        result = self.runner.invoke(self.command, [mock_ip])
        # Assert the result
        self.assertIn(mock_ip, result.output)

    def test_private_ip_error(self) -> None:
        """Test for private ip."""
        # Mock the arguments
        mock_ip = "192.168.1.1"
        # Run the command
        result = self.runner.invoke(self.command, [mock_ip])
        # Assert the result
        self.assertIn(PRIVATE_IP_SKIP_MESSAGE, result.output)

    @patch("valkyrie_tools.ipcheck.get_ip_info")
    def test_multiple_ip(self, mock_get_ip_info: MagicMock) -> None:
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

    @patch("valkyrie_tools.ipcheck.get_ip_info")
    def test_get_ip_info_returns_none(
        self, mock_get_ip_info: MagicMock
    ) -> None:
        """Test that a None result from get_ip_info is skipped silently."""
        mock_get_ip_info.return_value = None
        result = self.runner.invoke(self.command, ["1.2.3.4"])
        self.assertEqual(result.exit_code, 0)


class TestIpcheckJson(unittest.TestCase):
    """JSON output tests for ipcheck command."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        from click.testing import CliRunner

        self.runner = CliRunner()

    @patch("valkyrie_tools.ipcheck.get_ip_info")
    def test_json_single_public_ip(self, mock_get_ip_info: MagicMock) -> None:
        """Test --json output for a single public IP."""
        mock_get_ip_info.return_value = {
            "hostname": "one.one.one.one",
            "city": "Sydney",
        }
        result = self.runner.invoke(cli, ["--json", "1.1.1.1"])
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["input"], "1.1.1.1")
        self.assertEqual(data[0]["hostname"], "one.one.one.one")

    def test_json_private_ip_becomes_error_entry(self) -> None:
        """Test that a private IP produces an error entry in JSON mode."""
        result = self.runner.invoke(cli, ["--json", "192.168.1.1"])
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertEqual(data[0]["input"], "192.168.1.1")
        self.assertEqual(data[0]["error"], PRIVATE_IP_SKIP_MESSAGE)

    @patch("valkyrie_tools.ipcheck.get_ip_info")
    def test_json_none_result_becomes_error_entry(
        self, mock_get_ip_info: MagicMock
    ) -> None:
        """Test that a None get_ip_info result becomes an error entry."""
        mock_get_ip_info.return_value = None
        result = self.runner.invoke(cli, ["--json", "1.2.3.4"])
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertEqual(data[0]["error"], "No data returned.")

    def test_json_piped_dnscheck_output(self) -> None:
        """Test that dnscheck JSON piped to ipcheck is handled correctly."""
        upstream = json.dumps(
            [
                {
                    "input": "example.com",
                    "records": {"A": ["1.2.3.4"], "AAAA": []},
                }
            ]
        )
        with patch("valkyrie_tools.ipcheck.get_ip_info") as mock_info:
            mock_info.return_value = {"city": "NYC"}
            result = self.runner.invoke(cli, ["--json"], input=upstream)
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertEqual(data[0]["input"], "1.2.3.4")

    def test_json_piped_unrecognised_schema_raises(self) -> None:
        """Test that unrecognised piped JSON raises a UsageError."""
        upstream = json.dumps([{"foo": "bar"}])
        result = self.runner.invoke(cli, ["--json"], input=upstream)
        self.assertNotEqual(result.exit_code, 0)


class TestJsonExtractorIpcheck(unittest.TestCase):
    """Unit tests for json_extractor_ipcheck."""

    def test_extracts_a_and_aaaa(self) -> None:
        """Test that A and AAAA records are extracted."""
        data = [
            {
                "input": "example.com",
                "records": {"A": ["1.2.3.4"], "AAAA": ["::1"]},
            }
        ]
        result = json_extractor_ipcheck(data)
        self.assertIn("1.2.3.4", result)
        self.assertIn("::1", result)

    def test_deduplicates_ips(self) -> None:
        """Test that duplicate IPs across entries are deduplicated."""
        data = [
            {"input": "a.com", "records": {"A": ["1.2.3.4"]}},
            {"input": "b.com", "records": {"A": ["1.2.3.4"]}},
        ]
        result = json_extractor_ipcheck(data)
        self.assertEqual(result.count("1.2.3.4"), 1)

    def test_unrecognised_schema_raises(self) -> None:
        """Test that missing 'records' key raises ValueError."""
        with self.assertRaises(ValueError):
            json_extractor_ipcheck([{"input": "example.com"}])

    def test_empty_list_returns_empty_tuple(self) -> None:
        """Test that an empty list returns an empty tuple."""
        result = json_extractor_ipcheck([])
        self.assertEqual(result, ())
