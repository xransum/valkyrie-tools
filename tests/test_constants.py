"""Constants test module."""

import unittest

from valkyrie_tools.constants import (
    DOMAIN_REGEX,
    EMAIL_ADDR_REGEX,
    IPV4_REGEX,
    IPV6_REGEX,
    URL_REGEX,
)


class TestRegex(unittest.TestCase):
    """Test regex."""

    def setUp(self: unittest.TestCase) -> None:
        """Set up test fixtures, if any."""
        pass

    def test_url_regex(self: unittest.TestCase) -> None:
        """Test url regex."""
        self.assertIsNotNone(URL_REGEX.match("https://www.google.com"))
        self.assertIsNone(URL_REGEX.match("not a url"))

    def test_domain_regex(self: unittest.TestCase) -> None:
        """Test domain regex."""
        self.assertIsNotNone(DOMAIN_REGEX.match("google.com"))
        self.assertIsNone(DOMAIN_REGEX.match("not a domain"))

    def test_email_addr_regex(self: unittest.TestCase) -> None:
        """Test email address regex."""
        self.assertIsNotNone(EMAIL_ADDR_REGEX.match("test@gmail.com"))
        self.assertIsNone(EMAIL_ADDR_REGEX.match("not an email"))

    def test_ipv4_addr_regex(self: unittest.TestCase) -> None:
        """Test ipv4 address regex."""
        self.assertIsNotNone(IPV4_REGEX.match("192.168.1.1"))
        self.assertIsNone(IPV4_REGEX.match("not an ip address"))

    def test_ipv6_addr_regex(self: unittest.TestCase) -> None:
        """Test ipv6 address regex."""
        self.assertIsNotNone(
            IPV6_REGEX.match("2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        )
        self.assertIsNone(IPV6_REGEX.match("not an ip address"))
