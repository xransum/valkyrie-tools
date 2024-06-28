"""Whois utility functions."""

from time import sleep
from typing import Optional, Union

import ipwhois
import whois
from ipwhois import IPWhois


__all__ = [
    "get_whois",
    "get_ip_whois",
]

WHOIS_MAX_RETRIES = 3


def get_whois(
    domain: str,
) -> Optional[Union[whois.parser.WhoisCom, whois.parser.WhoisEntry]]:
    """Get whois information for a domain."""
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


def get_ip_whois(ipaddr: str) -> Optional[dict]:
    """Get ip whois information for a valid ip addr."""
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
