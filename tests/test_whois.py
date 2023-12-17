"""Test suite for the valkyrie_tools.whois module."""
import unittest
from unittest.mock import patch

import whois

from valkyrie_tools.whois import WHOIS_MAX_RETRIES, get_ip_whois, get_whois


class TestGetWhois(unittest.TestCase):
    """Test suite for the get_whois function."""

    @patch("valkyrie_tools.whois.whois.whois")
    def test_get_whois_successful(self, mock_whois):
        """Test get_whois successfully retrieves whois information."""
        # Arrange
        mock_value = "example.com"
        mock_valid_result = {"domain": mock_value}
        mock_whois.return_value = mock_valid_result
        # Act
        result = get_whois(mock_value)
        # Assert
        self.assertEqual(result, mock_valid_result)

    @patch("valkyrie_tools.whois.whois.whois")
    def test_get_whois_failure(self, mock_whois):
        """Test get_whois failure to retrieve whois information."""
        # Arrange
        mock_value = "example.com"
        mock_whois.side_effect = whois.parser.PywhoisError
        # Act
        result = get_whois(mock_value)
        # Assert
        self.assertIsNone(result)

    @patch("valkyrie_tools.whois.whois.whois")
    @patch("valkyrie_tools.whois.sleep", return_value=None)
    def test_get_whois_successful_retried(self, mock_sleep, mock_whois):
        """Test get_whois successfully after 1 retry."""
        # Arrange
        mock_value = "example.com"
        mock_valid_result = {"domain": mock_value}
        mock_whois.side_effect = [
            None,
            mock_valid_result,
        ]
        # Act
        result = get_whois(mock_value)
        # Assert
        self.assertEqual(result, mock_valid_result)
        mock_sleep.assert_called_once()

    @patch("valkyrie_tools.whois.whois.whois")
    @patch("valkyrie_tools.whois.sleep", return_value=None)
    def test_get_whois_max_retries_exceeded(self, mock_sleep, mock_whois):
        """Test get_whois fails to get whois info after max retries."""
        # Arrange
        mock_result = None
        mock_whois.side_effect = [mock_result] * (WHOIS_MAX_RETRIES + 1)
        # Act
        result = get_whois("example.com")
        # Assert
        self.assertIsNone(result)
        # mock_sleep.assert_called()
        self.assertEqual(mock_sleep.call_count, WHOIS_MAX_RETRIES)


class TestGetIPWhois(unittest.TestCase):
    """Test class for the get_ip_whois function."""

    @patch("ipwhois.IPWhois.lookup_whois")
    def test_get_ip_whois_success(self, mock_lookup_whois):
        """Test get_ip_whois function successfully retrieves whois info."""
        # Arrange
        mock_lookup_whois.return_value = {"test": "data"}
        ipaddr = "8.8.8.8"
        # Act
        result = get_ip_whois(ipaddr)
        # Assert
        self.assertEqual(result, {"test": "data"})
        mock_lookup_whois.assert_called_once_with(
            retry_count=0, asn_methods=["dns", "whois", "http"]
        )

    @patch("ipwhois.IPWhois.lookup_whois")
    def test_get_ip_whois_failure(self, mock_lookup_whois):
        """Test get_ip_whois function when it fails to retrieve whois info."""
        # Arrange
        mock_lookup_whois.side_effect = ValueError("Test error")
        ipaddr = "8.8.8.8"
        # Act
        result = get_ip_whois(ipaddr)
        # Assert
        self.assertIsNone(result)
        mock_lookup_whois.assert_called_once_with(
            retry_count=0, asn_methods=["dns", "whois", "http"]
        )
