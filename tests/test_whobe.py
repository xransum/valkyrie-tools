"""Unittests for the whobe cli command."""

import json
import unittest
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, patch

from valkyrie_tools.whobe import (
    NO_WHOIS_MSG,
    cli,
    domain_whois_to_dict,
    ip_whois_to_dict,
    json_extractor_whobe,
    print_ip_whois,
)

from .test_base_command import BaseCommandTest

whois_keys = [
    "domain_name",
    "registrar",
    "whois_server",
    "referral_url",
    "updated_date",
    "creation_date",
    "expiration_date",
    "name_servers",
    "status",
    "emails",
    "dnssec",
    "name",
    "org",
    "address",
    "city",
    "state",
    "registrant_postal_code",
    "country",
]
whois_ip_keys = [
    "nir",
    "asn_registry",
    "asn",
    "asn_cidr",
    "asn_country_code",
    "asn_date",
    "asn_description",
    "query",
    "nets",
    "raw",
    "referral",
    "raw_referral",
]


class TestWhobe(BaseCommandTest, unittest.TestCase):
    """Test suite for whobe command."""

    command = cli

    def setUp(self) -> None:
        """Set up test fixtures, if any."""
        super().setUp()

        self.mock_whois_data: Dict[str, Any] = {
            key: "Hello, World!" for key in whois_keys
        }
        self.mock_whois_ip_data: Dict[str, Any] = {
            key: "Hello, World!" for key in whois_ip_keys
        }
        self.mock_whois_ip_data["nets"] = []

    def tearDown(self) -> None:
        """Tear down test fixtures, if any."""
        super().tearDown()

    @patch("valkyrie_tools.whobe.get_ip_whois")
    def test_ip_whois(self, mock_get_ip_whois: MagicMock) -> None:
        """Test ip address."""
        mock_ip_addr = "192.168.1.1"
        mock_result = self.mock_whois_ip_data.copy()
        mock_result["query"] = mock_ip_addr
        mock_get_ip_whois.return_value = mock_result
        result = self.runner.invoke(cli, [mock_ip_addr])
        self.assertIn("> %s" % mock_ip_addr, result.output)
        self.assertIn("Hello, World!", result.output)
        self.assertEqual(result.exit_code, 0)

    @patch("valkyrie_tools.whobe.get_ip_whois")
    def test_ip_whois_none(self, mock_get_ip_whois: MagicMock) -> None:
        """Test ip address."""
        mock_ip_addr = "192.168.1.1"
        mock_get_ip_whois.return_value = None
        result = self.runner.invoke(cli, [mock_ip_addr])
        self.assertIn("> %s" % mock_ip_addr, result.output)
        self.assertIn(NO_WHOIS_MSG, result.output)
        self.assertEqual(result.exit_code, 0)

    @patch("valkyrie_tools.whobe.get_whois")
    def test_whois(self, mock_get_whois: MagicMock) -> None:
        """Test domain whois."""
        mock_domain = "example.com"
        mock_result = self.mock_whois_data.copy()
        mock_result["domain_name"] = mock_domain
        mock_get_whois.return_value = mock_result
        result = self.runner.invoke(cli, [mock_domain])
        self.assertIn("> %s" % mock_domain, result.output)
        self.assertIn("Hello, World!", result.output)
        self.assertEqual(result.exit_code, 0)

    @patch("valkyrie_tools.whobe.get_whois")
    def test_whois_none(self, mock_get_whois: MagicMock) -> None:
        """Test domain whois."""
        mock_domain = "example.com"
        mock_get_whois.return_value = None
        result = self.runner.invoke(cli, [mock_domain])
        self.assertIn("> %s" % mock_domain, result.output)
        self.assertIn(NO_WHOIS_MSG, result.output)
        self.assertEqual(result.exit_code, 0)

    @patch("valkyrie_tools.whobe.get_whois")
    def test_whois_multiple_domains(self, mock_get_whois: MagicMock) -> None:
        """Test domain whois."""
        mock_domains = ["example.com", "www.example.com"]
        mock_base_result = self.mock_whois_data

        def side_effect() -> Generator[Dict[str, Any], None, None]:
            for d in range(len(mock_domains)):
                mock_domain = mock_domains[d]
                mock_result = mock_base_result.copy()
                mock_result["domain_name"] = mock_domain
                yield mock_result

        mock_get_whois.side_effect = side_effect()
        result = self.runner.invoke(cli, mock_domains)

        for mock_domain in mock_domains:
            self.assertIn("> %s" % mock_domain, result.output)

        self.assertIn("Hello, World!", result.output)
        self.assertEqual(result.exit_code, 0)

    @patch("valkyrie_tools.whobe.click.echo")
    def test_print_ip_whois_with_no_data(self, mock_echo: MagicMock) -> None:
        """Test print_ip_whois with no data."""
        # Arrange
        mock_whois_data = None
        mock_expected_output = "No whois data."
        # Act
        print_ip_whois(mock_whois_data)
        # Assert
        mock_echo.assert_called_once_with(mock_expected_output, err=True)


class TestWhobeJson(unittest.TestCase):
    """JSON output tests for whobe command."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        from click.testing import CliRunner

        self.runner = CliRunner()

    @patch("valkyrie_tools.whobe.get_ip_whois")
    def test_json_ip_address(self, mock_get_ip_whois: MagicMock) -> None:
        """Test --json output for an IP address."""
        mock_get_ip_whois.return_value = {
            "asn": "15169",
            "asn_country_code": "US",
            "asn_cidr": "8.8.8.0/24",
            "nets": [],
        }
        result = self.runner.invoke(cli, ["--json", "8.8.8.8"])
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertIsInstance(data, list)
        self.assertEqual(data[0]["input"], "8.8.8.8")
        self.assertEqual(data[0]["type"], "ip")
        self.assertEqual(data[0]["asn"], "15169")

    @patch("valkyrie_tools.whobe.get_ip_whois")
    def test_json_ip_none_result(self, mock_get_ip_whois: MagicMock) -> None:
        """Test that a None IP whois result produces an error entry."""
        mock_get_ip_whois.return_value = None
        result = self.runner.invoke(cli, ["--json", "8.8.8.8"])
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertIn("error", data[0])

    @patch("valkyrie_tools.whobe.get_whois")
    def test_json_domain(self, mock_get_whois: MagicMock) -> None:
        """Test --json output for a domain."""
        mock_get_whois.return_value = {
            "registrar": "Example Registrar",
            "emails": ["admin@example.com"],
            "name_servers": ["ns1.example.com"],
        }
        result = self.runner.invoke(cli, ["--json", "example.com"])
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertEqual(data[0]["input"], "example.com")
        self.assertEqual(data[0]["type"], "domain")
        self.assertEqual(data[0]["registrar"], "Example Registrar")

    @patch("valkyrie_tools.whobe.get_whois")
    def test_json_domain_none_result(self, mock_get_whois: MagicMock) -> None:
        """Test that a None domain whois result produces an error entry."""
        mock_get_whois.return_value = None
        result = self.runner.invoke(cli, ["--json", "example.com"])
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertIn("error", data[0])

    @patch("valkyrie_tools.whobe.get_whois")
    def test_json_piped_input_extractor(
        self, mock_get_whois: MagicMock
    ) -> None:
        """Test that upstream JSON is parsed via the extractor."""
        mock_get_whois.return_value = {"registrar": "R"}
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


class TestIpWhoisToDict(unittest.TestCase):
    """Unit tests for ip_whois_to_dict helper."""

    def test_returns_error_when_whois_is_none(self) -> None:
        """Test that None whois produces an error entry."""
        result = ip_whois_to_dict("8.8.8.8", None)
        self.assertEqual(result["input"], "8.8.8.8")
        self.assertEqual(result["type"], "ip")
        self.assertIn("error", result)

    def test_returns_error_when_whois_not_dict(self) -> None:
        """Test that a non-dict whois produces an error entry."""
        result = ip_whois_to_dict("8.8.8.8", "bad value")  # type: ignore[arg-type]
        self.assertIn("error", result)

    def test_filters_nets_without_name_or_handle(self) -> None:
        """Test that nets without name/handle are excluded."""
        whois = {
            "asn": "15169",
            "asn_country_code": "US",
            "asn_cidr": "8.8.8.0/24",
            "nets": [
                {
                    "name": "GOGL",
                    "handle": "GOGL-1",
                    "cidr": "8.8.8.0/24",
                    "range": None,
                    "address": None,
                    "city": None,
                    "country": None,
                    "postal_code": None,
                    "emails": [],
                },
                {"name": None, "handle": None},  # should be excluded
            ],
        }
        result = ip_whois_to_dict("8.8.8.8", whois)
        self.assertEqual(len(result["nets"]), 1)
        self.assertEqual(result["nets"][0]["name"], "GOGL")

    def test_net_with_none_cidr_has_null_hosts(self) -> None:
        """Test that a net with no cidr gets None for hosts."""
        whois = {
            "asn": "1",
            "asn_country_code": "US",
            "asn_cidr": "1.0.0.0/8",
            "nets": [
                {
                    "name": "NET",
                    "handle": "NET-1",
                    "cidr": None,
                    "range": None,
                    "address": None,
                    "city": None,
                    "country": None,
                    "postal_code": None,
                    "emails": [],
                },
            ],
        }
        result = ip_whois_to_dict("1.1.1.1", whois)
        self.assertIsNone(result["nets"][0]["hosts"])


class TestDomainWhoisToDict(unittest.TestCase):
    """Unit tests for domain_whois_to_dict helper."""

    def test_returns_error_when_whois_is_none(self) -> None:
        """Test that None whois produces an error entry."""
        result = domain_whois_to_dict("example.com", None)
        self.assertEqual(result["input"], "example.com")
        self.assertEqual(result["type"], "domain")
        self.assertIn("error", result)

    def test_returns_error_when_whois_not_dict(self) -> None:
        """Test that a non-dict whois produces an error entry."""
        result = domain_whois_to_dict("example.com", "bad")  # type: ignore[arg-type]
        self.assertIn("error", result)

    def test_emails_str_converted_to_list(self) -> None:
        """Test that a string emails value is wrapped in a list."""
        result = domain_whois_to_dict(
            "example.com", {"emails": "admin@example.com", "name_servers": []}
        )
        self.assertIsInstance(result["emails"], list)
        self.assertIn("admin@example.com", result["emails"])

    def test_name_servers_str_converted_to_list(self) -> None:
        """Test that a string name_servers value is wrapped in a list."""
        result = domain_whois_to_dict(
            "example.com", {"emails": [], "name_servers": "ns1.example.com"}
        )
        self.assertIsInstance(result["name_servers"], list)
        self.assertIn("ns1.example.com", result["name_servers"])

    def test_empty_name_servers_defaults_to_empty_list(self) -> None:
        """Test that None name_servers produces an empty list."""
        result = domain_whois_to_dict(
            "example.com", {"emails": [], "name_servers": None}
        )
        self.assertEqual(result["name_servers"], [])


class TestJsonExtractorWhobe(unittest.TestCase):
    """Unit tests for json_extractor_whobe."""

    def test_extracts_input_fields(self) -> None:
        """Test that 'input' fields are extracted."""
        data = [{"input": "example.com"}, {"input": "8.8.8.8"}]
        result = json_extractor_whobe(data)
        self.assertEqual(result, ("example.com", "8.8.8.8"))

    def test_unrecognised_schema_raises(self) -> None:
        """Test that missing 'input' key raises ValueError."""
        with self.assertRaises(ValueError):
            json_extractor_whobe([{"type": "domain"}])

    def test_empty_list_returns_empty_tuple(self) -> None:
        """Test that an empty list returns an empty tuple."""
        result = json_extractor_whobe([])
        self.assertEqual(result, ())
