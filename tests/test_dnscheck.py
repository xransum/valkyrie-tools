"""Tests for dnscheck module."""

import json
import unittest
from unittest.mock import MagicMock, patch

from valkyrie_tools.dnscheck import (
    build_dns_result,
    cli,
    json_extractor_dnscheck,
)

from .test_base_command import BaseCommandTest


class TestDnscheck(BaseCommandTest, unittest.TestCase):
    """Test suite for dnscheck command."""

    command = cli

    def setUp(self) -> None:
        """Set up test fixtures, if any."""
        super().setUp()

    def tearDown(self) -> None:
        """Tear down test fixtures, if any."""
        super().tearDown()

    def test_successful(self) -> None:
        """Test for success."""
        # Mock the arguments
        mock_ip = "1.1.1.1"
        # Run the command
        result = self.runner.invoke(self.command, [mock_ip])
        # Assert the result
        self.assertIn(mock_ip, result.output)

    @patch("valkyrie_tools.dnscheck.get_dns_records")
    def test_no_record_types(self, mock_get_dns_records: MagicMock) -> None:
        """Test for no record types."""
        # Mock the responses
        # We need to test the flag for rtypes, passing an empty
        # list of record types, which should revert to the default
        pass

    @patch("valkyrie_tools.dnscheck.get_dns_records")
    def test_multiple_ip(self, mock_get_dns_records: MagicMock) -> None:
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


class TestDnscheckJson(unittest.TestCase):
    """JSON output tests for dnscheck command."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        from click.testing import CliRunner

        self.runner = CliRunner()

    @patch("valkyrie_tools.dnscheck.get_dns_records")
    def test_json_single_domain(self, mock_get_dns_records: MagicMock) -> None:
        """Test --json output for a single domain."""
        mock_get_dns_records.return_value = [("A", "1.2.3.4")]
        result = self.runner.invoke(cli, ["--json", "example.com"])
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertIsInstance(data, list)
        self.assertEqual(data[0]["input"], "example.com")
        self.assertIn("A", data[0]["records"])
        self.assertIn("1.2.3.4", data[0]["records"]["A"])

    @patch("valkyrie_tools.dnscheck.get_dns_records")
    def test_json_multiple_records_grouped(
        self, mock_get_dns_records: MagicMock
    ) -> None:
        """Test that multiple record types are grouped under 'records'."""
        mock_get_dns_records.return_value = [
            ("A", "1.2.3.4"),
            ("MX", "mail.example.com"),
        ]
        result = self.runner.invoke(cli, ["--json", "example.com"])
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        records = data[0]["records"]
        self.assertIn("A", records)
        self.assertIn("MX", records)

    @patch("valkyrie_tools.dnscheck.get_dns_records")
    def test_json_piped_input_extractor(
        self, mock_get_dns_records: MagicMock
    ) -> None:
        """Test that an upstream JSON array is parsed via the extractor."""
        mock_get_dns_records.return_value = [("A", "5.6.7.8")]
        upstream = json.dumps([{"input": "example.com"}])
        result = self.runner.invoke(cli, ["--json"], input=upstream)
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertEqual(data[0]["input"], "example.com")

    def test_json_piped_unrecognised_schema_raises(self) -> None:
        """Test that unrecognised piped JSON causes a non-zero exit."""
        upstream = json.dumps([{"foo": "bar"}])
        result = self.runner.invoke(cli, ["--json"], input=upstream)
        self.assertNotEqual(result.exit_code, 0)


class TestBuildDnsResult(unittest.TestCase):
    """Unit tests for build_dns_result helper."""

    def test_groups_by_record_type(self) -> None:
        """Test that records are grouped by type."""
        result = build_dns_result(
            "example.com",
            [("A", "1.2.3.4"), ("A", "5.6.7.8"), ("MX", "mail.example.com")],
        )
        self.assertEqual(result["input"], "example.com")
        self.assertEqual(result["records"]["A"], ["1.2.3.4", "5.6.7.8"])
        self.assertEqual(result["records"]["MX"], ["mail.example.com"])

    def test_empty_results(self) -> None:
        """Test that an empty result list produces an empty records dict."""
        result = build_dns_result("example.com", [])
        self.assertEqual(result["records"], {})


class TestJsonExtractorDnscheck(unittest.TestCase):
    """Unit tests for json_extractor_dnscheck."""

    def test_extracts_input_fields(self) -> None:
        """Test that 'input' fields are extracted."""
        data = [{"input": "example.com"}, {"input": "1.2.3.4"}]
        result = json_extractor_dnscheck(data)
        self.assertEqual(result, ("example.com", "1.2.3.4"))

    def test_unrecognised_schema_raises(self) -> None:
        """Test that missing 'input' key raises ValueError."""
        with self.assertRaises(ValueError):
            json_extractor_dnscheck([{"records": {}}])

    def test_empty_list_returns_empty_tuple(self) -> None:
        """Test that an empty list returns an empty tuple."""
        result = json_extractor_dnscheck([])
        self.assertEqual(result, ())
