"""Test for valkyrie_tools.dns module."""

import unittest
from unittest.mock import Mock, patch

import dns.resolver

from valkyrie_tools.dns import (
    RECORD_TYPES,
    get_dns_record,
    get_dns_records,
    get_rdns_record,
    is_valid_record_type,
)


class TestValidRecordType(unittest.TestCase):
    """Test function is valid record type."""

    def test_valid_record_type(self):
        """Test valid record type."""
        for record_type_name in RECORD_TYPES:
            self.assertTrue(is_valid_record_type(record_type_name))

    def test_invalid_record_type(self):
        """Test invalid record type."""
        for record_type_name in ["INVALID", "INVALID2", "", None]:
            self.assertFalse(is_valid_record_type(record_type_name))


class TestGetRdnsRecord(unittest.TestCase):
    """Test function get reverse DNS record."""

    def test_is_valid_ip_addr_exception(self):
        """Test value error."""
        # Mock the values
        mock_values = ["invalid", "invalid2", ""]

        # Run the function
        for mock_value in mock_values:
            with self.assertRaises(ValueError):
                get_rdns_record(mock_value)

    @patch("valkyrie_tools.dns.dns.resolver.Resolver")
    @patch("valkyrie_tools.dns.is_valid_ip_addr")
    def test_successful(
        self,
        mock_is_valid_ip_addr: Mock,
        mock_resolver: Mock,
    ) -> None:
        """Test get reverse DNS record."""
        # Mock the values
        mock_ip_addr = "192.168.1.1"
        mock_result = ("PTR", "example.com")

        # Mock the results
        mock_is_valid_ip_addr.return_value = True

        mock_results = Mock()
        mock_results.rdtype.name = mock_result[0]
        mock_results.to_text.return_value = mock_result[1]

        mock_resolve = Mock()
        mock_resolve.resolve.return_value = [mock_results]
        mock_resolver.return_value = mock_resolve

        # Run the function
        result = get_rdns_record(mock_ip_addr)

        # Assert the result
        self.assertEqual(result, [mock_result])

    @patch("valkyrie_tools.dns.dns.resolver.Resolver")
    @patch("valkyrie_tools.dns.is_valid_ip_addr")
    def test_exceptions(
        self,
        mock_is_valid_ip_addr: Mock,
        mock_resolver: Mock,
    ) -> None:
        """Test get reverse DNS record."""
        # Mock the values
        mock_ip_addr = "192.168.1.1"
        mock_result = []
        mock_side_effects = [
            dns.exception.SyntaxError,
            dns.resolver.NXDOMAIN,
            dns.resolver.NoAnswer,
        ]

        # Mock the results
        mock_is_valid_ip_addr.return_value = True
        mock_resolve = Mock()
        mock_resolve.resolve.side_effect = mock_side_effects

        # Iterate over the exceptions
        for _ in mock_side_effects:
            mock_resolver.return_value = mock_resolve
            # Run the function
            result = get_rdns_record(mock_ip_addr)
            # Assert the result
            self.assertEqual(result, mock_result)


class TestGetDnsRecord(unittest.TestCase):
    """Test function get DNS record."""

    @patch("valkyrie_tools.dns.is_valid_record_type")
    def test_is_valid_record_type_exception(
        self,
        mock_is_valid_record_type: Mock,
    ) -> None:
        """Test value error."""
        # Mock the values
        mock_rdtype = "A"
        mock_values = ["invalid", "invalid2"]

        # Mock the results
        mock_is_valid_record_type.side_effect = [False] * len(mock_values)

        for mock_value in mock_values:
            # Assert the exception
            with self.assertRaises(ValueError):
                # Run the function
                get_dns_record(mock_value, record_type=mock_rdtype)

    @patch("valkyrie_tools.dns.is_valid_record_type")
    @patch("valkyrie_tools.dns.is_valid_ip_addr")
    @patch("valkyrie_tools.dns.dns.resolver.Resolver")
    def test_successful(
        self,
        mock_resolver: Mock,
        mock_is_valid_ip_addr: Mock,
        mock_is_valid_record_type: Mock,
    ) -> None:
        """Test get DNS record."""
        # Mock the values
        mock_domain = "example.com"
        mock_result = ("A", "192.168.1.1")

        # Mock the results
        mock_is_valid_record_type.return_value = True
        mock_is_valid_ip_addr.return_value = True

        mock_record = Mock()
        mock_record.rdtype.name = mock_result[0]
        mock_record.to_text.return_value = mock_result[1]

        mock_resolve = Mock()
        mock_resolve.resolve.return_value = [mock_record]
        mock_resolver.return_value = mock_resolve

        # Run the function
        result = get_dns_record(mock_domain, record_type=mock_result[0])

        # Assert the result
        self.assertEqual(result, [mock_result])

    @patch("valkyrie_tools.dns.is_valid_record_type")
    @patch("valkyrie_tools.dns.is_valid_ip_addr")
    @patch("valkyrie_tools.dns.dns.resolver.Resolver")
    def test_successful_ptr(
        self,
        mock_resolver: Mock,
        mock_is_valid_ip_addr: Mock,
        mock_is_valid_record_type: Mock,
    ) -> None:
        """Test get DNS record."""
        # Mock the values
        mock_ip_addr = "192.168.1.1"
        mock_result = ("PTR", "example.com")

        # Mock the results
        mock_is_valid_record_type.return_value = True
        mock_is_valid_ip_addr.return_value = True

        mock_record = Mock()
        mock_record.rdtype.name = mock_result[0]
        mock_record.to_text.return_value = mock_result[1]

        mock_resolve = Mock()
        mock_resolve.resolve.return_value = [mock_record]
        mock_resolver.return_value = mock_resolve

        # Run the function
        result = get_dns_record(mock_ip_addr, record_type=mock_result[0])

        # Assert the result
        self.assertEqual(result, [mock_result])

    @patch("valkyrie_tools.dns.is_valid_record_type")
    @patch("valkyrie_tools.dns.is_valid_ip_addr")
    @patch("valkyrie_tools.dns.dns.resolver.Resolver")
    def test_mx_record_parse(
        self,
        mock_resolver: Mock,
        mock_is_valid_ip_addr: Mock,
        mock_is_valid_record_type: Mock,
    ) -> None:
        """Test get DNS record."""
        # Mock the values
        mock_domain = "example.com"
        mock_record_type = "MX"
        mock_record_values = [
            (mock_record_type, "10 mail.%s" % mock_domain),
            (mock_record_type, "10 ."),
        ]
        mock_result = (mock_record_type, "mail.%s" % mock_domain)

        # Mock the results
        mock_is_valid_record_type.return_value = True
        mock_is_valid_ip_addr.return_value = True

        mock_records = []
        for record_value in mock_record_values:
            mock_record = Mock()
            mock_record.rdtype.name = record_value[0]
            mock_record.to_text.return_value = record_value[1]
            mock_records.append(mock_record)

        mock_resolve = Mock()
        mock_resolve.resolve.return_value = mock_records
        mock_resolver.return_value = mock_resolve

        # Run the function
        result = get_dns_record(mock_domain, record_type=mock_record_type)

        # Assert the result
        self.assertEqual(result, [mock_result])

    @patch("valkyrie_tools.dns.is_valid_record_type")
    @patch("valkyrie_tools.dns.is_valid_ip_addr")
    @patch("valkyrie_tools.dns.dns.resolver.Resolver")
    def test_exceptions(
        self,
        mock_resolver: Mock,
        mock_is_valid_ip_addr: Mock,
        mock_is_valid_record_type: Mock,
    ) -> None:
        """Test get DNS record."""
        # Mock the values
        mock_domain = "example.com"
        mock_result = ("A", "192.168.1.1")
        mock_side_effects = [
            dns.exception.SyntaxError,
            dns.resolver.NXDOMAIN,
            dns.resolver.NoAnswer,
        ]

        # Mock the results
        mock_is_valid_record_type.return_value = True
        mock_is_valid_ip_addr.return_value = True

        mock_resolve = Mock()
        mock_resolve.resolve.side_effect = mock_side_effects
        mock_resolver.return_value = mock_resolve

        # Iterate over the exceptions
        for _ in mock_side_effects:
            # Run the function
            result = get_dns_record(mock_domain, record_type=mock_result[0])
            # Assert the result
            self.assertEqual(result, [])


class TestGetDnsRecords(unittest.TestCase):
    """Test function get DNS records."""

    @patch("valkyrie_tools.dns.get_dns_record")
    def test_successful(
        self,
        mock_get_dns_record: Mock,
    ) -> None:
        """Test get DNS records."""
        # Mock the values
        mock_domain = "example.com"
        mock_record_types = ["A", "MX"]
        mock_results = {
            "A": [("A", "192.168.1.1")],
            "MX": [("MX", "10 mail.example.com")],
        }

        # Mock the results
        mock_get_dns_record.side_effect = (
            lambda domain, record_type: mock_results[record_type]
        )

        # Run the function
        result = get_dns_records(mock_domain, record_types=mock_record_types)

        # Assert the result
        self.assertEqual(
            result,
            list(mock_results.values())[0] + list(mock_results.values())[1],
        )
