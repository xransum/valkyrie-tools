"""Unittests for the whobe cli command."""
import unittest
from unittest.mock import Mock, patch
from click.testing import CliRunner

from valkyrie_tools.whobe import (
    NO_WHOIS_MSG,
    cli,
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
        super().setUp()

        """Set up test fixtures, if any."""
        self.mock_whois_data = dict(
            [(key, "Hello, World!") for key in whois_keys]
        )
        self.mock_whois_ip_data = dict(
            [(key, "Hello, World!") for key in whois_ip_keys]
        )
        self.mock_whois_ip_data["nets"] = []

    def tearDown(self) -> CliRunner:
        """Tear down test fixtures, if any."""
        super().tearDown()

    @patch("valkyrie_tools.whobe.get_ip_whois")
    def test_ip_whois(self, mock_get_ip_whois) -> None:
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
    def test_ip_whois_none(self, mock_get_ip_whois) -> None:
        """Test ip address."""
        mock_ip_addr = "192.168.1.1"
        mock_get_ip_whois.return_value = None
        result = self.runner.invoke(cli, [mock_ip_addr])
        self.assertIn("> %s" % mock_ip_addr, result.output)
        self.assertIn(NO_WHOIS_MSG, result.output)
        self.assertEqual(result.exit_code, 0)

    @patch("valkyrie_tools.whobe.get_whois")
    def test_whois(self, mock_get_whois) -> None:
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
    def test_whois_none(self, mock_get_whois) -> None:
        """Test domain whois."""
        mock_domain = "example.com"
        mock_get_whois.return_value = None
        result = self.runner.invoke(cli, [mock_domain])
        self.assertIn("> %s" % mock_domain, result.output)
        self.assertIn(NO_WHOIS_MSG, result.output)
        self.assertEqual(result.exit_code, 0)

    @patch("valkyrie_tools.whobe.get_whois")
    def test_whois_multiple_domains(self, mock_get_whois) -> None:
        """Test domain whois."""
        mock_domains = ["example.com", "www.example.com"]
        mock_base_result = self.mock_whois_data

        def side_effect():
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
    def test_print_ip_whois_with_no_data(self, mock_echo):
        # Arrange
        mock_whois_data = None
        mock_expected_output = "No whois data."
        # Act
        print_ip_whois(mock_whois_data)
        # Assert
        mock_echo.assert_called_once_with(mock_expected_output, err=True)
