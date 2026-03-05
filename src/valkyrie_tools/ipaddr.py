"""IP address utilities for valkyrie-tools.

Provides validators (:func:`is_ipv4_addr`, :func:`is_ipv6_addr`,
:func:`is_valid_ip_addr`, :func:`is_private_ip`, :func:`is_ip_in_cidr`) and
lookup helpers that query external sources for IP reputation data:

* **Tor** - :func:`get_tor_node_ip_addrs` / :func:`is_ip_tor_node`
* **ipinfo.io** - :func:`get_ip_info` (geolocation / ASN metadata)
* **AWS** - :func:`get_aws_ip_ranges` / :func:`is_aws_ip_addr`
* **Cloudflare** - :func:`get_cloudflare_ip_ranges` / :func:`is_cloudflare_ip_addr`
* **Fastly** - :func:`get_fastly_ip_ranges` / :func:`is_fastly_ip_addr`

Results from the remote endpoints are TTL-cached for 3600 seconds using
:data:`~valkyrie_tools.cache.cache`.
"""

import ipaddress
from typing import Any, Dict, List, Optional

import requests

from .cache import cache
from .constants import DEFAULT_REQUEST_TIMEOUT


# Global constants
PRIVATE_IP_CIDR_RANGES = [
    "10.0.0.0/8",  # Private-Use Networks - RFC1918
    "172.16.0.0/12",  # Private-Use Networks - RFC1918
    "192.168.0.0/16",  # Private-Use Networks - RFC1918
    "100.64.0.0/10",  # Shared Address Space - RFC6598
    "fc00::/7",  # IPv6 unique local addr (ULA) - RFC4193
]
"""CIDR ranges that are never publicly routable.

Includes:

* ``10.0.0.0/8``, ``172.16.0.0/12``, ``192.168.0.0/16`` - Private-use
  networks (RFC 1918).
* ``100.64.0.0/10`` - Shared address space for carrier-grade NAT (RFC 6598).
* ``fc00::/7`` - IPv6 Unique Local Addresses (RFC 4193).

Used by :func:`is_private_ip` to short-circuit lookups for non-public IPs.
"""
TOR_PROJECT_NODE_ENDPOINT = (
    "https://check.torproject.org/cgi-bin/TorBulkExitList.py"
)
"""URL of the Tor Project's bulk exit-node list (plain text, one IP per line)."""
IPINFO_API_ENDPOINT = "https://ipinfo.io/%s/json"
"""ipinfo.io JSON API endpoint template.  ``%s`` is replaced with the IP address."""
# https://docs.aws.amazon.com/vpc/latest/userguide/aws-ip-ranges.html#aws-ip-download
AWS_IP_RANGES_ENDPOINT = "https://ip-ranges.amazonaws.com/ip-ranges.json"
"""URL of the AWS public IP ranges JSON file."""
CLOUDFLARE_IPS_BASE_ENDPOINT = "https://www.cloudflare.com/ips-v%i/#"
"""Base URL template for Cloudflare IP range pages.  ``%i`` is replaced with
the IP version (``4`` or ``6``).
"""
CLOUDFLARE_IPV4_RANGES_ENDPOINT = CLOUDFLARE_IPS_BASE_ENDPOINT % 4
"""Cloudflare IPv4 range page URL (plain text, one CIDR per line)."""
CLOUDFLARE_IPV6_RANGES_ENDPOINT = CLOUDFLARE_IPS_BASE_ENDPOINT % 6
"""Cloudflare IPv6 range page URL (plain text, one CIDR per line)."""
FASTLY_IP_RANGES_ENDPOINT = "https://api.fastly.com/public-ip-list"
"""Fastly public IP list API endpoint (returns JSON)."""


def is_ipv4_addr(ipaddr: str) -> bool:
    """Check if a given ip addr is a valid ipv4 addr.

    Args:
        ipaddr (str): IP address to check.

    Returns:
        bool: True if ipaddr is a valid ipv4 addr.

    Example:
        >>> from valkyrie_tools.ipaddr import is_ipv4_addr
        >>> is_ipv4_addr("192.168.1.1")
        True
        >>> is_ipv4_addr("::1")
        False
    """
    if isinstance(ipaddr, str):
        try:
            ip = ipaddress.ip_address(ipaddr)
            return isinstance(ip, ipaddress.IPv4Address)
        except ValueError:
            return False

    return False


def is_ipv6_addr(ipaddr: str) -> bool:
    """Check if a given ip addr is a valid ipv6 addr.

    Args:
        ipaddr (str): IP address to check.

    Returns:
        bool: True if ipaddr is a valid ipv6 addr.

    Example:
        >>> from valkyrie_tools.ipaddr import is_ipv6_addr
        >>> is_ipv6_addr("::1")
        True
        >>> is_ipv6_addr("192.168.1.1")
        False
    """
    if isinstance(ipaddr, str):
        try:
            ip = ipaddress.ip_address(ipaddr)
            return isinstance(ip, ipaddress.IPv6Address)
        except ValueError:
            return False

    return False


def is_valid_ip_addr(ipaddr: str) -> bool:
    """Check if a given ip addr is a valid ipv4 or ipv6 addr.

    Args:
        ipaddr (str): IP address to check.

    Returns:
        bool: True if ipaddr is a valid ipv4 or ipv6 addr.
    """
    return any(
        [
            is_ipv4_addr(ipaddr),
            is_ipv6_addr(ipaddr),
        ]
    )


def is_private_ip(ipaddr: str) -> bool:
    """Check if ip addr is a private addr.

    Args:
        ipaddr (str): IP address to check.

    Returns:
        bool: True if ipaddr is a private addr.
    """
    try:
        ip = ipaddress.ip_address(ipaddr)
        return any(
            ip in ipaddress.ip_network(cidr) for cidr in PRIVATE_IP_CIDR_RANGES
        )
    except ValueError:
        return False


def get_net_size(cidr: str) -> int:
    """Get network size from cidr notation.

    Args:
        cidr (str): CIDR notation.

    Returns:
        int: Network size.
    """
    return int(cidr.split("/")[1])


def is_ip_in_cidr(ipaddr: str, cidr: str) -> bool:
    """Check if ip addr is in cidr range.

    Args:
        ipaddr (str): IP address to check.
        cidr (str): CIDR range to check.

    Returns:
        bool: True if ipaddr is in cidr range.

    Example:
        >>> from valkyrie_tools.ipaddr import is_ip_in_cidr
        >>> is_ip_in_cidr("10.0.0.5", "10.0.0.0/8")
        True
        >>> is_ip_in_cidr("8.8.8.8", "10.0.0.0/8")
        False
    """
    try:
        ip = ipaddress.ip_address(ipaddr)
        return ip in ipaddress.ip_network(cidr)
    except ValueError:
        return False


@cache.ttl_cache(maxsize=128, ttl=3600)
def get_tor_node_ip_addrs() -> List[str]:
    """Get a list of Tor exit-node IP addresses from the Tor Project.

    Results are TTL-cached for 3600 seconds (1 hour).  To force a fresh
    fetch, call :func:`is_ip_tor_node` with ``cached=False``, which invokes
    ``get_tor_node_ip_addrs.clear_cache()`` before this function.

    Returns:
        List[str]: A flat list of IPv4 address strings representing known
        Tor exit nodes, as published by the Tor Project bulk-exit-list
        endpoint.
    """
    r = requests.get(TOR_PROJECT_NODE_ENDPOINT, timeout=DEFAULT_REQUEST_TIMEOUT)
    r.raise_for_status()
    return [line for line in r.text.splitlines() if line != ""]


def is_ip_tor_node(ipaddr: str, cached: bool = True) -> bool:
    """Check if ip addr is a tor node.

    Args:
        ipaddr (str): IP address to check.
        cached (bool): When ``True`` (the default), the previously cached list
            of Tor exit-node addresses is reused.  Pass ``False`` to force a
            fresh fetch from the Tor Project endpoint.

    Returns:
        bool: True if ipaddr is a Tor exit node.
    """
    if cached is False:
        get_tor_node_ip_addrs.clear_cache()

    nodes = get_tor_node_ip_addrs()
    return ipaddr in nodes


def get_ip_info(ipaddr: str) -> Optional[dict]:
    """Get geolocation and network metadata for an IP address.

    Queries the ipinfo.io JSON API.  Only valid IP addresses (as determined
    by :func:`is_valid_ip_addr`) are looked up; invalid input returns
    ``None`` immediately without making a network request.

    Args:
        ipaddr (str): A valid IPv4 or IPv6 address string.

    Returns:
        Optional[dict]: A dictionary of IP metadata (keys include ``ip``,
        ``hostname``, ``city``, ``region``, ``country``, ``loc``, ``org``,
        ``postal``, ``timezone``) on success, or ``None`` if ``ipaddr`` is
        not a valid IP address.
    """
    if is_valid_ip_addr(ipaddr):
        r = requests.get(
            IPINFO_API_ENDPOINT % ipaddr, timeout=DEFAULT_REQUEST_TIMEOUT
        )
        r.raise_for_status()
        return r.json()

    return None


@cache.ttl_cache(maxsize=128, ttl=3600)
def get_aws_ip_ranges() -> Optional[Dict[str, Any]]:
    """Get the public IP ranges published by AWS.

    Fetches the AWS IP ranges JSON from
    :data:`AWS_IP_RANGES_ENDPOINT` and flattens both IPv4 and IPv6 prefixes
    into a single list of dicts.  Each dict has a ``"prefix"`` key (the CIDR
    string) plus all other metadata fields from the original prefix record
    (e.g. ``"region"``, ``"service"``).  Results are TTL-cached for 3600
    seconds (1 hour).

    Returns:
        Optional[List[dict]]: A flat list of prefix metadata dicts on
        success, or ``None`` if the endpoint returns a non-2xx HTTP status.
    """
    try:
        r = requests.get(
            AWS_IP_RANGES_ENDPOINT, timeout=DEFAULT_REQUEST_TIMEOUT
        )
        r.raise_for_status()
        result = r.json()
        cidrs = []
        for key in ["ip_prefix", "ipv6_prefix"]:
            prefixes = result.get("%ses" % key.replace("ip_", ""))
            for prefix in prefixes:
                cidr = prefix.get(key)
                del prefix[key]
                prefix["prefix"] = cidr
            cidrs.extend(prefixes)
        return cidrs
    except requests.exceptions.HTTPError:
        return None


def is_aws_ip_addr(ipaddr: str) -> bool:
    """Check if ip addr is an AWS ip.

    Args:
        ipaddr (str): IP address to check.

    Returns:
        bool: True if ipaddr is an AWS ip.
    """
    try:
        ip = ipaddress.ip_address(ipaddr)
        return any(  # pragma: no cover
            ip in ipaddress.ip_network(cidr) for cidr in get_aws_ip_ranges()
        )
    except ValueError:
        return False


def get_cloudflare_range(endpoint: str) -> Optional[List[str]]:
    """Fetch a plain-text list of IP CIDR ranges from a Cloudflare endpoint.

    Args:
        endpoint (str): URL of a Cloudflare IP-list endpoint (one range per
            line in plain text).  Typically one of
            :data:`CLOUDFLARE_IPV4_RANGES_ENDPOINT` or
            :data:`CLOUDFLARE_IPV6_RANGES_ENDPOINT`.

    Returns:
        Optional[List[str]]: A list of CIDR strings parsed from the response
        body.  Returns an empty list if the request fails with an HTTP error.
    """
    results = []
    try:
        r = requests.get(endpoint, timeout=DEFAULT_REQUEST_TIMEOUT)
        r.raise_for_status()
        subnets = [line for line in r.text.split("\n") if line.strip() != ""]
        results.extend(subnets)
    except requests.exceptions.HTTPError:
        pass

    return results


@cache.ttl_cache(maxsize=128, ttl=3600)
def get_cloudflare_ip_ranges() -> Optional[Dict[str, Any]]:
    """Get the combined IPv4 and IPv6 IP ranges published by Cloudflare.

    Calls :func:`get_cloudflare_range` for both
    :data:`CLOUDFLARE_IPV4_RANGES_ENDPOINT` and
    :data:`CLOUDFLARE_IPV6_RANGES_ENDPOINT` and merges the results.
    Results are TTL-cached for 3600 seconds (1 hour).

    Returns:
        Optional[List[str]]: A flat list of CIDR strings covering all
        Cloudflare-announced IPv4 and IPv6 ranges.  Returns an empty list
        if both endpoint requests fail.
    """
    ip_ranges = []

    ip_ranges.extend(
        [
            *get_cloudflare_range(CLOUDFLARE_IPV4_RANGES_ENDPOINT),
            *get_cloudflare_range(CLOUDFLARE_IPV6_RANGES_ENDPOINT),
        ]
    )

    return ip_ranges


def is_cloudflare_ip_addr(ipaddr: str) -> bool:
    """Check if ip addr is a cloudflare ip.

    Args:
        ipaddr (str): IP address to check.

    Returns:
        bool: True if ipaddr is a Cloudflare ip.
    """
    try:
        ip = ipaddress.ip_address(ipaddr)
        return any(  # pragma: no cover
            ip in ipaddress.ip_network(cidr)
            for cidr in get_cloudflare_ip_ranges()
        )
    except ValueError:
        return False


@cache.ttl_cache(maxsize=128, ttl=3600)
def get_fastly_ip_ranges() -> Optional[Dict[str, Any]]:
    """Get the public IP ranges published by Fastly.

    Fetches the Fastly public IP list JSON from
    :data:`FASTLY_IP_RANGES_ENDPOINT`.  Results are TTL-cached for 3600
    seconds (1 hour).

    Returns:
        Optional[List[str]]: A list of CIDR strings covering all
        Fastly-announced IP ranges on success, or an empty list if the
        endpoint returns a non-2xx HTTP status.
    """
    try:
        r = requests.get(
            FASTLY_IP_RANGES_ENDPOINT, timeout=DEFAULT_REQUEST_TIMEOUT
        )
        r.raise_for_status()
        result = r.json()
        return [subnet for subnet in result.values()]
    except requests.exceptions.HTTPError:
        return []


def is_fastly_ip_addr(ipaddr: str) -> bool:
    """Check if ip addr is a fastly ip.

    Args:
        ipaddr (str): IP address to check.

    Returns:
        bool: True if ipaddr is a fastly ip.
    """
    try:
        ip = ipaddress.ip_address(ipaddr)
        return any(  # pragma: no cover
            ip in ipaddress.ip_network(cidr) for cidr in get_fastly_ip_ranges()
        )
    except ValueError:
        return False
