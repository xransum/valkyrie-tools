"""Module for IP address manipulation."""
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
TOR_PROJECT_NODE_ENDPOINT = (
    "https://check.torproject.org/cgi-bin/TorBulkExitList.py"
)
IPINFO_API_ENDPOINT = "https://ipinfo.io/%s/json"
# https://docs.aws.amazon.com/vpc/latest/userguide/aws-ip-ranges.html#aws-ip-download
AWS_IP_RANGES_ENDPOINT = "https://ip-ranges.amazonaws.com/ip-ranges.json"
CLOUDFLARE_IPS_BASE_ENDPOINT = "https://www.cloudflare.com/ips-v%i/#"
CLOUDFLARE_IPV4_RANGES_ENDPOINT = CLOUDFLARE_IPS_BASE_ENDPOINT % 4
CLOUDFLARE_IPV6_RANGES_ENDPOINT = CLOUDFLARE_IPS_BASE_ENDPOINT % 6
FASTLY_IP_RANGES_ENDPOINT = "https://api.fastly.com/public-ip-list"


def is_ipv4_addr(ipaddr: str) -> bool:
    """Check if a given ip addr is a valid ipv4 addr.

    Args:
        ipaddr (str): IP address to check.

    Returns:
        bool: True if ipaddr is a valid ipv4 addr.
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
    """
    try:
        ip = ipaddress.ip_address(ipaddr)
        return ip in ipaddress.ip_network(cidr)
    except ValueError:
        return False


@cache.ttl_cache(maxsize=128, ttl=3600)
def get_tor_node_ip_addrs() -> List[str]:
    """Get a list of tor node ip addresses.

    Returns:
        List[str]: List of tor node ip addresses.
    """
    r = requests.get(TOR_PROJECT_NODE_ENDPOINT, timeout=DEFAULT_REQUEST_TIMEOUT)
    r.raise_for_status()
    return [line for line in r.text.splitlines() if line != ""]


def is_ip_tor_node(ipaddr: str, cached: bool = True) -> bool:
    """Check if ip addr is a tor node.

    Args:
        ipaddr (str): IP address to check.
        cached (bool): Force refresh of cache. Defaults to False.

    Returns:
        bool: True if ipaddr is a tor node.
    """
    if cached is False:
        get_tor_node_ip_addrs.clear_cache()

    nodes = get_tor_node_ip_addrs()
    return ipaddr in nodes


def get_ip_info(ipaddr: str) -> Optional[dict]:
    """Get ip address info.

    Args:
        ipaddr (str): IP address to get info for.

    Returns:
        Optional[dict]: IP address info.
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
    """Get the public ip ranges for AWS services."""
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
    """Make request to endpoint and return only ip ranges."""
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
    """Get the public ip ranges for Cloudflare services."""
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
        bool: True if ipaddr is a fastly ip.
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
    """Get the public ip ranges for Fastly services."""
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
