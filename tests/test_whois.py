"""Test suite for the valkyrie_tools.whois module."""
import pytest
import whois
from unittest.mock import Mock, patch

from valkyrie_tools.whois import get_whois, get_ip_whois



@patch('valkyrie_tools.whois.whois.whois')
def test_get_whois_success(mock_whois: Mock) -> None:
    """Test whois function success."""
    expected_data = {"domain": "example.com", "registrar": "Registrar, Inc."}
    mock_whois.return_value = expected_data

    result = get_whois("example.com")

    assert result == expected_data

@patch('valkyrie_tools.whois.whois.whois')
def test_get_whois_exception(mock_whois: Mock) -> None:
    """Test whois function exception."""
    mock_whois.side_effect = whois.parser.PywhoisError("Mocked PywhoisError")

    result = get_whois("invalid_domain")

    assert result is None


@patch('valkyrie_tools.whois.IPWhois')
def test_get_ip_whois_success(mock_IPWhois: Mock) -> None:
    """Test ip whois function success."""
    ipw_instance = mock_IPWhois.return_value
    ipw_instance.lookup_whois.return_value = {"mocked_data": "Hello World!"}

    result = get_ip_whois("192.168.1.1")

    assert result == {"mocked_data": "Hello World!"}


@patch('valkyrie_tools.whois.IPWhois')
def test_get_ip_whois_exception(mock_IPWhois: Mock) -> None:
    """Test ip whois function exception."""
    ipw_instance = mock_IPWhois.return_value
    ipw_instance.lookup_whois.side_effect = ValueError("Mocked ValueError")

    result = get_ip_whois("invalid_ip")

    assert result is None

