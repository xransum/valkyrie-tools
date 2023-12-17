import unittest
from unittest.mock import patch, MagicMock, Mock
import requests
from ipaddress import AddressValueError


from valkyrie_tools.constants import DEFAULT_REQUEST_TIMEOUT
from unittest.mock import patch
from valkyrie_tools.ipaddr import is_aws_ip_addr
from valkyrie_tools.ipaddr import (
    TOR_PROJECT_NODE_ENDPOINT,
    IPINFO_API_ENDPOINT,
    AWS_IP_RANGES_ENDPOINT,
    CLOUDFLARE_IPS_BASE_ENDPOINT,
    CLOUDFLARE_IPV4_RANGES_ENDPOINT,
    CLOUDFLARE_IPV6_RANGES_ENDPOINT,
    FASTLY_IP_RANGES_ENDPOINT,
    is_ipv4_addr,
    is_ipv6_addr,
    is_valid_ip_addr,
    is_private_ip,
    get_net_size,
    is_ip_in_cidr,
    get_tor_node_ip_addrs,
    is_ip_tor_node,
    get_ip_info,
    get_aws_ip_ranges,
    is_aws_ip_addr,
    get_cloudflare_range,
    get_cloudflare_ip_ranges,
    is_cloudflare_ip_addr,
    get_fastly_ip_ranges,
    is_fastly_ip_addr,
)


class TestIsIpv4Addr(unittest.TestCase):
    """Test case class for testing the `is_ipv4_addr` function."""

    def test_valid_ipv4_address(self):
        """Test case to check if the given IPv4 address is valid."""
        ipaddr = "192.168.0.1"
        result = is_ipv4_addr(ipaddr)
        self.assertTrue(result)

    def test_invalid_ipv4_address(self):
        """Returns False for invalid IPv4 addresses."""
        ipaddr = "256.0.0.1"
        result = is_ipv4_addr(ipaddr)
        self.assertFalse(result)

    def test_leading_zeros_ipv4_address(self):
        """Handles IPv4 addresses with leading zeros."""
        ipaddr = "001.002.003.004"
        result = is_ipv4_addr(ipaddr)
        self.assertFalse(result)

    def test_ipv6_address(self):
        """Returns False for IPv6 addresses."""
        ipaddr = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        result = is_ipv4_addr(ipaddr)
        self.assertFalse(result)

    def test_invalid_ip_address(self):
        """Returns False for an invalid IP address."""
        ipaddr = "foobar"
        result = is_ipv4_addr(ipaddr)
        self.assertFalse(result)

    def test_non_string_input(self):
        """Returns False for non-string input."""
        ipaddr = 12345
        result = is_ipv4_addr(ipaddr)
        self.assertFalse(result)

    def test_empty_string_input(self):
        """Returns False for empty string input."""
        ipaddr = ""
        result = is_ipv4_addr(ipaddr)
        self.assertFalse(result)


class TestIsIpv6Addr(unittest.TestCase):
    """Test case for the is_ipv6_addr function."""

    def test_valid_ipv6_address(self):
        """Returns True for a valid IPv6 address."""
        ipaddr = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        result = is_ipv6_addr(ipaddr)
        self.assertTrue(result)

    def test_invalid_ipv6_address(self):
        """Returns False for an invalid IPv6 address."""
        ipaddr = "2001:0db8:____::8a2e:0370:7334"
        result = is_ipv6_addr(ipaddr)
        self.assertFalse(result)

    def test_lowercase_hex_digits(self):
        """Accepts IPv6 addresses with lowercase hexadecimal digits."""
        ipaddr = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        result = is_ipv6_addr(ipaddr)
        self.assertTrue(result)

    def test_ipv4_address(self):
        """Returns False for an IPv4 address."""
        ipaddr = "192.168.0.1"
        result = is_ipv6_addr(ipaddr)
        self.assertFalse(result)

    def test_invalid_ip_address(self):
        """Returns False for an invalid IP address."""
        ipaddr = "foobar"
        result = is_ipv6_addr(ipaddr)
        self.assertFalse(result)


class TestIsValidIpAddr(unittest.TestCase):
    """Test the is_valid_ip_addr function."""

    def test_valid_ipv4_address(self):
        """Returns True for a valid IPv4 address."""
        ipaddr = "192.168.0.1"
        result = is_valid_ip_addr(ipaddr)
        self.assertTrue(result)

    def test_valid_ipv6_address(self):
        """Returns True for a valid IPv6 address."""
        ipaddr = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        result = is_valid_ip_addr(ipaddr)
        self.assertTrue(result)

    def test_invalid_ip_address(self):
        """Returns False for an invalid IP address."""
        ipaddr = "256.256.256.256"
        result = is_valid_ip_addr(ipaddr)
        self.assertFalse(result)

    def test_empty_string(self):
        """Returns False for an empty string."""
        ipaddr = ""
        result = is_valid_ip_addr(ipaddr)
        self.assertFalse(result)

    def test_whitespace_string(self):
        """Returns False for a string with only whitespace characters."""
        ipaddr = "   "
        result = is_valid_ip_addr(ipaddr)
        self.assertFalse(result)

    def test_multiple_ip_addresses(self):
        """Returns False for a string with more than one IP address."""
        ipaddr = "192.168.0.1 2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        result = is_valid_ip_addr(ipaddr)
        self.assertFalse(result)

    def test_invalid_ipv4_address(self):
        """Returns False for a string with an invalid IPv4 address."""
        ipaddr = "192.168.0.256"
        result = is_valid_ip_addr(ipaddr)
        self.assertFalse(result)

    def test_invalid_ipv6_address(self):
        """Returns False for a string with an invalid IPv6 address."""
        ipaddr = "2001:0db8:85a3:0000:0000:8a2e:0370:zzzz"
        result = is_valid_ip_addr(ipaddr)
        self.assertFalse(result)

    def test_ipv4_mapped_ipv6_address(self):
        """Returns False for a string with an IPv4-mapped IPv6 address."""
        ipaddr = "::ffff:192.168.0.1"
        result = is_valid_ip_addr(ipaddr)
        self.assertTrue(result)

    def test_valid_ipv4_address_with_leading_zeros(self):
        """Returns True for a string a valid IPv4 address and leading zeros."""
        ipaddr = "192.168.000.001"
        result = is_valid_ip_addr(ipaddr)
        self.assertFalse(result)

    def test_valid_ipv6_address_with_uppercase_letters(self):
        """Returns True for a valid IPv6 address and uppercase letters."""
        ipaddr = "2001:0DB8:85A3:0000:0000:8A2E:0370:7334"
        result = is_valid_ip_addr(ipaddr)
        self.assertTrue(result)

    def test_valid_ipv6_address_with_compressed_zeroes(self):
        """Returns True for a valid IPv6 address and compressed zeroes."""
        ipaddr = "2001:db8:85a3::8a2e:370:7334"
        result = is_valid_ip_addr(ipaddr)
        self.assertTrue(result)

    @patch("valkyrie_tools.ipaddr.isinstance")
    def test_value_isinstance_false(self, mock_isinstance):
        """Returns False when isinstance is False."""
        mock_isinstance.return_value = False
        # mock_isinstance.side_effect = False
        self.assertFalse(is_valid_ip_addr("192.168.1.1"))

    @patch("valkyrie_tools.ipaddr.ipaddress.ip_address")
    def test_value_value_error(self, mock_ip_address):
        """Returns False when isinstance is False."""
        # mock_isinstance.return_value = False
        mock = Mock(side_effect=ValueError("foo"))
        mock_ip_address.side_effect = mock
        self.assertFalse(is_valid_ip_addr("192.168.1.1"))


class TestIsPrivateIp(unittest.TestCase):
    """Test the is_private_ip function."""

    def test_private_ipv4_in_cidr_range(self):
        """True a private IPv4 address in a private CIDR range."""
        ipaddr = "192.168.0.1"
        result = is_private_ip(ipaddr)
        self.assertTrue(result)

    def test_private_ipv6_in_cidr_range(self):
        """True a private IPv6 address in a private CIDR range."""
        ipaddr = "fd00::1"
        result = is_private_ip(ipaddr)
        self.assertTrue(result)

    def test_public_ipv4_address(self):
        """False a public IPv4 address."""
        ipaddr = "8.8.8.8"
        result = is_private_ip(ipaddr)
        self.assertFalse(result)

    def test_ipv4_not_in_cidr_range(self):
        """False an IPv4 address that is not in a private CIDR range."""
        ipaddr = "123.123.123.123"
        result = is_private_ip(ipaddr)
        self.assertFalse(result)

    def test_ipv6_not_in_cidr_range(self):
        """False an IPv6 address that is not in a private CIDR range."""
        ipaddr = "2001:db8::1"
        result = is_private_ip(ipaddr)
        self.assertFalse(result)

    def test_ipv4_mapped_ipv6_not_in_cidr_range(self):
        """False an IPv4-mapped IPv6 address not in a private CIDR range."""
        ipaddr = "::ffff:192.0.2.1"
        result = is_private_ip(ipaddr)
        self.assertFalse(result)

    def test_private_ipv4_in_cidr_range(self):
        """True a private IPv4 address in a private CIDR range."""
        ipaddr = "192.168.0.1"
        result = is_private_ip(ipaddr)
        self.assertTrue(result)

    def test_private_ipv6_in_cidr_range(self):
        """True a private IPv6 address in a private CIDR range."""
        ipaddr = "fd00::1"
        result = is_private_ip(ipaddr)
        self.assertTrue(result)

    def test_invalid_ip_address(self):
        """False an invalid IP address string."""
        ipaddr = "invalid_ip_address"
        result = is_private_ip(ipaddr)
        self.assertFalse(result)

    def test_returns_false_for_public_ipv6_address(self):
        """False a public IPv6 address."""
        ipaddr = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        result = is_private_ip(ipaddr)
        self.assertFalse(result)

    def test_returns_false_for_public_ipv4_address(self):
        """False a public IPv4 address."""
        ipaddr = "203.0.113.1"
        result = is_private_ip(ipaddr)
        self.assertFalse(result)

    def test_returns_false_for_non_private_ipv4_address(self):
        """False an IPv4 address that is not in a private CIDR range."""
        ipaddr = "100.1.23.1"
        result = is_private_ip(ipaddr)
        self.assertFalse(result)

    def test_ipv6_not_in_cidr_range(self):
        """False an IPv6 address that is not in a private CIDR range."""
        ipaddr = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        result = is_private_ip(ipaddr)
        self.assertFalse(result)

    def test_ipv4_mapped_ipv6_not_in_cidr_range(self):
        """False an IPv4-mapped IPv6 address not in a private CIDR range."""
        ipaddr = "::ffff:192.0.2.1"
        result = is_private_ip(ipaddr)
        self.assertFalse(result)

    # False an IPv6 address a zone identifier that is not in a
    def test_ipv6_with_zone_identifier_not_in_private_cidr_range(self):
        """False an IPv6 address a zone identifier not in a private"""
        ipaddr = "2001:db8::1%eth0"
        result = is_private_ip(ipaddr)
        self.assertFalse(result)

    def test_private_ipv4_in_cidr_range(self):
        """Alt 1: Test a private IPv4 address in a private CIDR range."""
        ipaddr = "192.168.0.1"
        result = is_private_ip(ipaddr)
        self.assertTrue(result)

    def test_private_ipv4_in_cidr_range(self):
        """Alt 2: Test a different private IPv4 address in a private CIDR range."""
        ipaddr = "192.168.0.1"
        result = is_private_ip(ipaddr)
        self.assertTrue(result)

    def test_private_ipv4_in_different_cidr_range(self):
        """Alt 3: Test a private IPv4 address in a different private CIDR range."""
        ipaddr = "172.16.0.1"
        result = is_private_ip(ipaddr)
        self.assertTrue(result)

    def test_private_ipv4_in_multiple_cidr_ranges(self):
        """Alt 4: Test a private IPv4 address in multiple private CIDR ranges."""
        ipaddr = "192.168.0.1"
        result = is_private_ip(ipaddr)
        self.assertTrue(result)

    def test_private_ipv6_in_cidr_range(self):
        """Alt 1: Test a private IPv6 address in a private CIDR range."""
        ipaddr = "fd00::1"
        result = is_private_ip(ipaddr)
        self.assertTrue(result)

    def test_private_ipv6_in_cidr_range(self):
        """Alt 2: Test a different private IPv6 address in a private CIDR range."""
        ipaddr = "fd00::1"
        result = is_private_ip(ipaddr)
        self.assertTrue(result)

    def test_private_ipv6_in_different_cidr_range(self):
        """Alt 3: Test a private IPv6 address in a different private CIDR range."""
        ipaddr = "fd00::1"
        result = is_private_ip(ipaddr)
        self.assertTrue(result)

    def test_private_ipv6_in_multiple_cidr_ranges(self):
        """Alt 4: Test a private IPv6 address in multiple private CIDR ranges."""
        ipaddr = "fd00::1"
        result = is_private_ip(ipaddr)
        self.assertTrue(result)


class TestGetNetSize(unittest.TestCase):
    """Unit test class for get_net_size function."""

    def test_get_net_size_valid(self):
        """Test get_net_size with valid input."""
        self.assertEqual(get_net_size("192.168.1.0/24"), 24)

    def test_get_net_size_invalid(self):
        """Test get_net_size with invalid input."""
        with self.assertRaises(IndexError):
            get_net_size("192.168.1.0")

    def test_get_net_size_empty(self):
        """Test get_net_size with empty input."""
        with self.assertRaises(IndexError):
            get_net_size("")


class TestIsIpInCidr(unittest.TestCase):
    def test_valid_ip_in_cidr(self):
        """Test a valid IP in CIDR"""
        self.assertTrue(is_ip_in_cidr("192.168.1.1", "192.168.1.0/24"))

    def test_valid_ip_not_in_cidr(self):
        """Test a valid IP not in CIDR"""
        self.assertFalse(is_ip_in_cidr("192.168.2.1", "192.168.1.0/24"))

    def test_invalid_ip(self):
        """Test an invalid IP"""
        self.assertFalse(is_ip_in_cidr("999.999.999.999", "192.168.1.0/24"))

    def test_invalid_cidr(self):
        """Test an invalid CIDR"""
        self.assertFalse(is_ip_in_cidr("192.168.1.1", "999.999.999.999/24"))


class TestGetIpInfo(unittest.TestCase):
    """Test suite for get_ip_info function."""

    def setUp(self) -> None:
        """Set up test fixtures, if any."""
        pass

    def tearDown(self) -> None:
        """Tear down test fixtures, if any."""
        pass

    def test_get_ip_info(self):
        """Test get_ip_info function."""
        with patch("valkyrie_tools.ipaddr.requests.get") as mock_get:
            mock_ip = "192.168.1.1"
            mock_json_data = {"foo": mock_ip}
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_json_data
            mock_get.return_value = mock_response

            result = get_ip_info(mock_ip)

            self.assertEqual(result, mock_json_data)
            mock_get.assert_called_once_with(
                IPINFO_API_ENDPOINT % mock_ip, timeout=15
            )

    @patch("valkyrie_tools.ipaddr.is_valid_ip_addr")
    def test_get_ip_info_invalid_ip(self, mock_is_valid_ip_addr):
        """Test get_ip_info function woth invalid ip."""
        mock_is_valid_ip_addr.return_value = False
        result = get_ip_info("foo")

        self.assertEqual(result, None)

    @patch("valkyrie_tools.ipaddr.requests.get")
    def test_exception_on_status(self, mock_get):
        # Mock an error response
        mock_ip = "192.168.1.1"
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError("404 Client Error: Not Found")
        )

        # Ensure that raise_for_status is called when using the context manager
        mock_get.return_value = mock_response

        # Call the function that makes the request
        with self.assertRaises(requests.exceptions.HTTPError):
            result = get_ip_info(mock_ip)

        # Assertions
        mock_get.assert_called_once_with(
            IPINFO_API_ENDPOINT % mock_ip, timeout=DEFAULT_REQUEST_TIMEOUT
        )
        mock_response.raise_for_status.assert_called_once()


class TestGetTorNodeIpAddrs(unittest.TestCase):
    """Test the get_tor_node_ip_addrs function."""

    def setUp(self) -> None:
        """Set up test fixtures, if any."""
        # Clear function from cache
        get_tor_node_ip_addrs.clear_cache()

    def tearDown(self) -> None:
        """Tear down test fixtures, if any."""
        pass

    @patch("valkyrie_tools.ipaddr.requests.get")
    def test_get_tor_node_ip_addrs(self, mock_get):
        """
        Test get_tor_node_ip_addrs function.
        """
        # Arrange
        mock_results = ["1.2.3.4", "5.6.7.8"]
        mock_text = "\n".join(mock_results)
        mock_response = mock_get.return_value
        mock_response.text = mock_text

        # Act
        result = get_tor_node_ip_addrs()

        # Assert
        self.assertEqual(result, mock_results)
        mock_get.assert_called_once_with(
            TOR_PROJECT_NODE_ENDPOINT, timeout=DEFAULT_REQUEST_TIMEOUT
        )

    @patch("valkyrie_tools.ipaddr.requests.get")
    def test_get_tor_node_ip_addrs_http_error(self, mock_get):
        """Test the get_tor_node_ip_addrs function."""
        mock_get.return_value.raise_for_status.side_effect = (
            requests.exceptions.HTTPError
        )
        with self.assertRaises(requests.exceptions.HTTPError):
            get_tor_node_ip_addrs()

    @patch("requests.get")
    def test_get_tor_node_ip_addrs_cached(self, mock_get):
        """Test the get_tor_node_ip_addrs function caching."""
        # Arrange
        mock_results = ["1.2.3.4", "5.6.7.8"]
        mock_text = "\n".join(mock_results)
        mock_response = mock_get.return_value
        mock_response.text = mock_text

        # Act
        result = get_tor_node_ip_addrs()
        cached_result = get_tor_node_ip_addrs()

        # Assert
        self.assertEqual(result, mock_results)
        self.assertEqual(cached_result, mock_results)


class TestIsIpTorNode(unittest.TestCase):
    """Test the is_ip_tor_node function."""

    @patch("valkyrie_tools.ipaddr.get_tor_node_ip_addrs")
    def test_is_ip_tor_node(self, mock_get_tor_node_ip_addrs):
        """Test the is_ip_tor_node function."""
        # Arrange
        mock_results = ["1.2.3.4", "5.6.7.8"]
        mock_get_tor_node_ip_addrs.return_value = mock_results

        # Act
        result = is_ip_tor_node(mock_results[-1])

        # Assert
        self.assertTrue(result)

    @patch("valkyrie_tools.ipaddr.get_tor_node_ip_addrs")
    def test_is_ip_tor_node_false(self, mock_get_tor_node_ip_addrs):
        """Test the is_ip_tor_node function."""
        # Arrange
        mock_get_tor_node_ip_addrs.return_value = ["1.2.3.4", "5.6.7.8"]

        # Act
        result = is_ip_tor_node("0.0.0.0")

        # Assert
        self.assertFalse(result)


class TestIsIpTorNode(unittest.TestCase):
    @patch(
        "valkyrie_tools.ipaddr.get_tor_node_ip_addrs"
    )  # replace 'module_name' with the name of your module
    def test_ip_is_tor_node(self, mock_get_tor_node_ip_addrs):
        """Test for Tor node IP address."""
        # Arrange
        mock_get_tor_node_ip_addrs.return_value = [
            "192.0.2.0",
            "203.0.113.0",
            "198.51.100.0",
        ]
        # Act
        result = is_ip_tor_node("192.0.2.0")
        # Assert
        self.assertTrue(result)

    @patch("valkyrie_tools.ipaddr.get_tor_node_ip_addrs")
    def test_ip_is_not_tor_node(self, mock_get_tor_node_ip_addrs):
        """Test for non-Tor node IP address."""
        # Arrange
        mock_result = ["192.0.2.0", "203.0.113.0", "198.51.100.0"]
        mock_get_tor_node_ip_addrs.return_value = mock_result
        # Act
        result = is_ip_tor_node("192.0.2.1")
        # Assert
        self.assertFalse(result)

    @patch("valkyrie_tools.ipaddr.get_tor_node_ip_addrs")
    def test_cache_refresh(self, mock_get_tor_node_ip_addrs):
        """Test for Tor node IP address with cache refresh."""
        # Arrange
        mock_result = ["192.0.2.0", "203.0.113.0", "198.51.100.0"]
        mock_get_tor_node_ip_addrs.return_value = mock_result
        # Act
        result = is_ip_tor_node("192.0.2.0", cached=False)
        # Assert
        self.assertTrue(result)
        mock_get_tor_node_ip_addrs.clear_cache.assert_called_once()


class TestGetAwsIpRanges(unittest.TestCase):
    """Test suite for get_aws_ip_ranges function."""

    def setUp(self) -> None:
        """Set up test fixtures, if any."""
        self.mock_get_result = {
            "prefixes": [
                {
                    "ip_prefix": "1.1.1.1/26",
                    "region": "xx-abdef-n",
                    "service": "ABCDEF",
                    "network_border_group": "xx-abdef-n",
                }
            ],
            "ipv6_prefixes": [
                {
                    "ipv6_prefix": "2001:db8:1234:5678::/64",
                    "region": "xx-abdef-n",
                    "service": "ABCDEF",
                    "network_border_group": "xx-abdef-n",
                }
            ],
        }
        self.mock_result = [
            {
                "prefix": "1.1.1.1/26",
                "region": "xx-abdef-n",
                "service": "ABCDEF",
                "network_border_group": "xx-abdef-n",
            },
            {
                "prefix": "2001:db8:1234:5678::/64",
                "region": "xx-abdef-n",
                "service": "ABCDEF",
                "network_border_group": "xx-abdef-n",
            },
        ]
        get_aws_ip_ranges.clear_cache()

    def tearDown(self) -> None:
        """Tear down test fixtures, if any."""
        pass

    @patch("valkyrie_tools.ipaddr.requests.get")
    def test_get_aws_ip_ranges(self, mock_get):
        """Test the get_aws_ip_ranges function."""
        # Arrange
        mock_get.return_value.json.return_value = self.mock_get_result
        # Act
        result = get_aws_ip_ranges()
        # Assert
        self.assertEqual(len(result), len(self.mock_get_result))
        mock_get.assert_called_once_with(
            AWS_IP_RANGES_ENDPOINT, timeout=DEFAULT_REQUEST_TIMEOUT
        )

    @patch("valkyrie_tools.ipaddr.requests.get")
    def test_get_aws_ip_ranges_http_error(self, mock_get):
        """Test get_aws_ip_ranges function with HTTPError."""
        # Arrange
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError
        )
        mock_get.return_value = mock_response
        # Act
        result = get_aws_ip_ranges()
        # Assert
        self.assertIsNone(result)


class TestIsAwsIpAddr(unittest.TestCase):
    """Test the is_aws_ip_addr function."""

    def setUp(self) -> None:
        """
        Set up test fixtures, if any.
        """
        self.mock_results = [
            "192.0.2.0/24",
            "198.51.100.0/24",
            "2001:db8::/32",
            "2001:db8:1234:5678::/64",
        ]
        get_aws_ip_ranges.clear_cache()

    @patch("valkyrie_tools.ipaddr.get_aws_ip_ranges")
    def test_is_aws_ipv4_addr(self, mock_get_aws_ip_ranges):
        """Test the is_aws_ip_addr function."""
        # Arrange
        mock_get_aws_ip_ranges.return_value = self.mock_results
        # Act
        result = is_aws_ip_addr("192.0.2.1")
        # Assert
        self.assertTrue(result)

    @patch("valkyrie_tools.ipaddr.get_aws_ip_ranges")
    def test_is_aws_ipv6_addr(self, mock_get_aws_ip_ranges):
        """Test the is_aws_ip_addr function."""
        # Arrange
        mock_get_aws_ip_ranges.return_value = self.mock_results
        # Act
        result = is_aws_ip_addr("2001:db8::1")
        # Assert
        self.assertTrue(result)

    @patch("valkyrie_tools.ipaddr.get_aws_ip_ranges")
    def test_is_aws_invalid_ip_addr(self, mock_get_aws_ip_ranges):
        """Test the is_aws_ip_addr function."""
        # Arrange
        mock_get_aws_ip_ranges.return_value = self.mock_results
        # Act
        result = is_aws_ip_addr("foo")
        # Assert
        self.assertFalse(result)


class TestGetCloudflareRange(unittest.TestCase):
    """Test case class for testing the `get_cloudflare_range` function."""

    @patch("valkyrie_tools.ipaddr.requests.get")
    def test_successful_request(self, mock_get):
        """Test case to check if the function makes a successful request."""
        endpoint = "https://example.com"
        mock_response = MagicMock()
        mock_response.text = "192.0.2.0/24\n198.51.100.0/24\n203.0.113.0/24"
        mock_get.return_value = mock_response

        result = get_cloudflare_range(endpoint)

        mock_get.assert_called_once_with(
            endpoint, timeout=DEFAULT_REQUEST_TIMEOUT
        )
        self.assertEqual(
            result, ["192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"]
        )

    @patch("valkyrie_tools.ipaddr.requests.get")
    def test_failed_request(self, mock_get):
        """Test case to check if the function handles a failed request."""
        endpoint = "https://example.com"
        mock_get.side_effect = requests.exceptions.HTTPError("404 Not Found")

        result = get_cloudflare_range(endpoint)

        mock_get.assert_called_once_with(
            endpoint, timeout=DEFAULT_REQUEST_TIMEOUT
        )
        self.assertEqual(result, [])

    @patch("valkyrie_tools.ipaddr.requests.get")
    def test_empty_response(self, mock_get):
        """Test case to check if the function handles an empty response."""
        endpoint = "https://example.com"
        mock_response = MagicMock()
        mock_response.text = ""
        mock_get.return_value = mock_response

        result = get_cloudflare_range(endpoint)

        mock_get.assert_called_once_with(
            endpoint, timeout=DEFAULT_REQUEST_TIMEOUT
        )
        self.assertEqual(result, [])


class TestGetCloudflareIpRanges(unittest.TestCase):
    """
    Test class for the get_cloudflare_ip_ranges function.
    """

    def setUp(self) -> None:
        """
        Set up test fixtures, if any.
        """
        self.mock_ipv4_result = ["192.0.2.0/24", "198.51.100.0/24"]
        self.mock_ipv6_result = ["2001:db8::/32", "2001:db8:1234:5678::/64"]
        get_cloudflare_ip_ranges.clear_cache()

    @patch("valkyrie_tools.ipaddr.get_cloudflare_range")
    def test_get_cloudflare_ip_ranges_success(self, mock_get_cloudflare_range):
        """
        Test get_cloudflare_ip_ranges function when it successfully retrieves IP
        ranges.
        """
        # Arrange
        mock_results = [self.mock_ipv4_result[:], self.mock_ipv6_result[:]]
        mock_get_cloudflare_range.side_effect = mock_results
        # Act
        result = get_cloudflare_ip_ranges()
        # Assert
        self.assertEqual(
            result, [subnet for subnets in mock_results for subnet in subnets]
        )

    @patch("valkyrie_tools.ipaddr.get_cloudflare_range")
    def test_get_cloudflare_ip_ranges_failure(self, mock_get_cloudflare_range):
        """
        Test get_cloudflare_ip_ranges function when it fails to retrieve IP ranges.
        """
        # Arrange
        mock_get_cloudflare_range.return_value = []
        # Act
        result = get_cloudflare_ip_ranges()
        # Assert
        self.assertEqual(result, [])
        for endpoint in [
            CLOUDFLARE_IPV4_RANGES_ENDPOINT,
            CLOUDFLARE_IPV6_RANGES_ENDPOINT,
        ]:
            mock_get_cloudflare_range.assert_any_call(endpoint)

    @patch("valkyrie_tools.ipaddr.requests.get")
    def test_clear_cache(self, mock_get):
        """
        Test clearing the cache for get_cloudflare_ip_ranges.
        """
        # Act
        get_cloudflare_ip_ranges.clear_cache()

        # Assert
        # Ensure that requests.get was not called during cache clearing
        mock_get.assert_not_called()


class TestIsCloudflareIpAddr(unittest.TestCase):
    """Test the is_cloudflare_ip_addr function."""

    def setUp(self) -> None:
        """
        Set up test fixtures, if any.
        """
        self.mock_ipv4_result = ["192.0.2.0/24", "198.51.100.0/24"]
        self.mock_ipv6_result = ["2001:db8::/32", "2001:db8:1234:5678::/64"]
        self.mock_results = [
            self.mock_ipv4_result[:],
            self.mock_ipv6_result[:],
        ]
        get_cloudflare_ip_ranges.clear_cache()

    @patch("valkyrie_tools.ipaddr.get_cloudflare_range")
    def test_is_cloudflare_ipv4_addr(self, mock_get_cloudflare_range):
        """Test the is_cloudflare_ip_addr function."""
        # Arrange
        mock_get_cloudflare_range.side_effect = self.mock_results
        # Act
        result = is_cloudflare_ip_addr("192.0.2.1")
        # Assert
        self.assertTrue(result)

    @patch("valkyrie_tools.ipaddr.get_cloudflare_range")
    def test_is_cloudflare_ipv6_addr(self, mock_get_cloudflare_range):
        """Test the is_cloudflare_ip_addr function."""
        # Arrange
        mock_get_cloudflare_range.side_effect = self.mock_results
        # Act
        result = is_cloudflare_ip_addr("2001:db8::1")
        # Assert
        self.assertTrue(result)

    @patch("valkyrie_tools.ipaddr.get_cloudflare_range")
    def test_is_cloudflare_invalid_ip_addr(self, mock_get_cloudflare_range):
        """Test the is_cloudflare_ip_addr function."""
        # Arrange
        mock_get_cloudflare_range.side_effect = self.mock_results
        # Act
        result = is_cloudflare_ip_addr("foo")
        # Assert
        self.assertFalse(result)

    @patch("valkyrie_tools.ipaddr.ipaddress")
    def test_is_cloudflare_value_error(self, mock_ipaddress):
        """Test the is_cloudflare_ip_addr function."""
        # Arrange
        mock = Mock(side_effect=ValueError("foo"))
        mock_ipaddress.ip_address.side_effect = mock
        # Act
        result = is_cloudflare_ip_addr("0.0.0.0")
        # Assert
        self.assertFalse(result)


class TestGetFastlyIpRanges(unittest.TestCase):
    """
    Test class for the get_fastly_ip_ranges function.
    """

    def setUp(self) -> None:
        """
        Set up test fixtures, if any.
        """
        self.mock_ipv4_result = ["192.0.2.0/24", "198.51.100.0/24"]
        self.mock_ipv6_result = ["2001:db8::/32", "2001:db8:1234:5678::/64"]
        self.mock_results = {
            "addresses": self.mock_ipv4_result[:],
            "ipv6_addresses": self.mock_ipv6_result[:],
        }
        get_fastly_ip_ranges.clear_cache()

    @patch("valkyrie_tools.ipaddr.requests.get")
    def test_get_fastly_ip_ranges_success(self, mock_get):
        """
        Test get_fastly_ip_ranges function when it successfully retrieves IP
        ranges.
        """
        # Arrange
        mock_get.return_value.json.side_effect = [self.mock_results]
        # Act
        result = get_fastly_ip_ranges()
        # Assert
        self.assertEqual(result, list(self.mock_results.values()))

    @patch("valkyrie_tools.ipaddr.requests.get")
    def test_get_fastly_ip_ranges_failure(self, mock_get):
        """
        Test get_fastly_ip_ranges function when it fails to retrieve IP ranges.
        """
        # Arrange
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError
        )
        mock_get.return_value = mock_response

        # Act
        result = get_fastly_ip_ranges()

        # Assert
        self.assertEqual(result, [])
        mock_get.assert_called_once_with(
            FASTLY_IP_RANGES_ENDPOINT, timeout=DEFAULT_REQUEST_TIMEOUT
        )
        mock_response.raise_for_status.assert_called_once()

    @patch("valkyrie_tools.ipaddr.requests.get")
    def test_clear_cache(self, mock_get):
        """
        Test clearing the cache for get_fastly_ip_ranges.
        """
        # Act
        get_fastly_ip_ranges.clear_cache()
        # Assert
        mock_get.assert_not_called()


class TestIsFastlyIpAddr(unittest.TestCase):
    """Test the is_fastly_ip_addr function."""

    def setUp(self) -> None:
        """
        Set up test fixtures, if any.
        """
        self.mock_results = [
            "192.0.2.0/24",
            "198.51.100.0/24",
            "2001:db8::/32",
            "2001:db8:1234:5678::/64",
        ]
        get_fastly_ip_ranges.clear_cache()

    @patch("valkyrie_tools.ipaddr.get_fastly_ip_ranges")
    def test_is_fastly_ipv4_addr(self, mock_get_fastly_ip_ranges):
        """Test the is_fastly_ip_addr function."""
        # Arrange
        mock_get_fastly_ip_ranges.return_value = self.mock_results
        # Act
        result = is_fastly_ip_addr("192.0.2.1")
        # Assert
        self.assertTrue(result)

    @patch("valkyrie_tools.ipaddr.get_fastly_ip_ranges")
    def test_is_fastly_ipv6_addr(self, mock_get_fastly_ip_ranges):
        """Test the is_fastly_ip_addr function."""
        # Arrange
        mock_get_fastly_ip_ranges.return_value = self.mock_results
        # Act
        result = is_fastly_ip_addr("2001:db8::1")
        # Assert
        self.assertTrue(result)

    @patch("valkyrie_tools.ipaddr.get_fastly_ip_ranges")
    def test_is_fastly_invalid_ip_addr(self, mock_get_fastly_ip_ranges):
        """Test the is_fastly_ip_addr function."""
        # Arrange
        mock_get_fastly_ip_ranges.return_value = self.mock_results
        # Act
        result = is_fastly_ip_addr("foo")
        # Assert
        self.assertFalse(result)
