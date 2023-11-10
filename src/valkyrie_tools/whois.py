"""Whois utility functions."""
from typing import Optional, Union

import whois
from ipwhois import IPWhois

__all__ = ["get_whois", "get_ip_whois"]


def get_whois(
    domain: str,
) -> Optional[Union[whois.parser.WhoisCom, whois.parser.WhoisEntry]]:
    """Get whois information for a domain."""
    w = None
    try:
        w = whois.whois(domain)
        # if w["domain"] is None:
        #     w = None
    except whois.parser.PywhoisError:
        w = None

    return w


def get_ip_whois(ipaddr: str) -> Optional[dict]:
    """Get ip whois information for a valid ip addr."""
    results = None
    try:
        ipw = IPWhois(ipaddr)
        results = ipw.lookup_whois(retry_count=0, asn_methods=["dns", "whois", "http"])
        # results = ipw.lookup_rdap()
    except ValueError:
        results = None

    return results
