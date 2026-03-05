"""Whois utility functions."""

from time import sleep
from typing import Any, Dict, Optional, Union

import ipwhois  # type: ignore[import-untyped]
import whois  # type: ignore[import-untyped]
from ipwhois import IPWhois


__all__ = [
    "get_whois",
    "get_ip_whois",
]

WHOIS_MAX_RETRIES = 3
"""Maximum number of WHOIS query attempts in :func:`get_whois`.

On each attempt the result is checked for the queried domain name; if the
check fails the function sleeps ``0.25 * attempt`` seconds before retrying.
"""


def get_whois(
    domain: str,
) -> Optional[Union[whois.parser.WhoisCom, whois.parser.WhoisEntry]]:
    """Get WHOIS information for a domain name.

    Queries the WHOIS service for the given domain.  The lookup is retried up
    to :data:`WHOIS_MAX_RETRIES` times with an exponential back-off of
    ``0.25 * attempt`` seconds between retries, stopping early when the
    returned record confirms the queried domain name.

    Args:
        domain (str): The fully-qualified domain name to look up
            (e.g. ``"example.com"``).

    Returns:
        Optional[Union[whois.parser.WhoisCom, whois.parser.WhoisEntry]]:
        A parsed WHOIS record on success, or ``None`` if the domain could not
        be resolved or the WHOIS service returned an error
        (:class:`whois.parser.PywhoisError` is caught silently).

    Example:
        >>> from valkyrie_tools.whois import get_whois
        >>> result = get_whois("example.com")
        >>> result is not None  # doctest: +SKIP
        True
    """
    w = None
    try:
        attempts = 0
        while attempts < WHOIS_MAX_RETRIES:
            attempts += 1
            w = whois.whois(domain)

            if w is not None and domain in w.get("domain", []):
                break

            sleep(0.25 * attempts)
    except whois.parser.PywhoisError:
        w = None

    return w


def get_ip_whois(ipaddr: str) -> Optional[Dict[str, Any]]:
    """Get WHOIS information for an IP address.

    Performs a WHOIS lookup via :class:`ipwhois.IPWhois`, querying ASN data
    through DNS, WHOIS, and HTTP fallbacks in that order.

    Args:
        ipaddr (str): A valid public IPv4 or IPv6 address to look up.
            Private and reserved addresses (as defined by
            :data:`~valkyrie_tools.ipaddr.PRIVATE_IP_CIDR_RANGES`) will
            cause an :class:`ipwhois.exceptions.IPDefinedError` which is
            caught and returns ``None``.

    Returns:
        Optional[dict]: A dictionary containing ASN details, network ranges,
        and contact information as returned by
        ``IPWhois.lookup_whois()``, or ``None`` if ``ipaddr`` is invalid
        (:class:`ValueError`) or is a defined/reserved address
        (:class:`ipwhois.exceptions.IPDefinedError`).

    Example:
        >>> from valkyrie_tools.whois import get_ip_whois
        >>> result = get_ip_whois("8.8.8.8")
        >>> result is not None  # doctest: +SKIP
        True
        >>> result.get("asn_description") is not None  # doctest: +SKIP
        True
    """
    results = None
    try:
        ipw = IPWhois(ipaddr)
        results = ipw.lookup_whois(
            retry_count=0, asn_methods=["dns", "whois", "http"]
        )
        # results = ipw.lookup_rdap()
    except (ValueError, ipwhois.exceptions.IPDefinedError):
        results = None

    return results
