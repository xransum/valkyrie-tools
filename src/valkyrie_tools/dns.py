"""Module for DNS lookups."""

import re
from typing import List, Tuple

import dns.inet
import dns.name
import dns.query
import dns.rdatatype
import dns.resolver
import dns.tsig
import dns.tsigkeyring
import dns.update

from .ipaddr import is_valid_ip_addr


Timeout = dns.resolver.Timeout
DEFAULT_NAMESERVERS = [
    "1.1.1.1",
    "1.0.0.1",  # Cloudflare
    "8.8.8.8",
    "8.8.4.4",  # Google
    "9.9.9.9",
    "149.112.112.112",  # Quad9
    "208.67.222.222",
    "208.67.220.220",  # OpenDNS
    "8.26.56.26",
    "8.20.247.20",  # Comodo Secure
    "185.225.168.168",
    "185.228.169.168",  # CleanBrowsing
    "76.76.19.19",
    "76.223.122.150",  # Alternate
    "176.103.130.130",
    "176.103.130.131",  # AdGuard
    "64.6.64.6",
    "64.6.65.6",  # Verisign
]
DEFAULT_RECORD_TYPES = ["A", "AAAA", "MX", "CNAME", "PTR"]
RECORD_TYPES = [q.name for q in dns.rdatatype.RdataType]


def is_valid_record_type(record_type: str) -> bool:
    """Check if a given record type is valid.

    Args:
        record_type (str): Record type to check.

    Returns:
        bool: True if record_type is a valid record type.
    """
    try:
        return dns.rdatatype.from_text(record_type) is not None

    except (dns.rdatatype.UnknownRdatatype, AttributeError):
        return False


def get_rdns_record(ipaddr: str) -> list:
    """Get reverse DNS record for an IP address.

    Args:
        ipaddr (str): IP address to get reverse DNS record for.

    Returns:
        list: List of reverse DNS records.

    Raises:
        ValueError: If the IP address is invalid.
    """
    if is_valid_ip_addr(ipaddr) is False:
        raise ValueError(f"Invalid IP address: {ipaddr}")

    # Configure DNS resolver with default name servers
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = DEFAULT_NAMESERVERS
    resolver.search = []

    try:
        # Retrieve reverse DNS records for the IP address
        records = resolver.resolve(dns.reversename.from_address(ipaddr), "PTR")
        return [(record.rdtype.name, record.to_text()) for record in records]
    except (
        dns.exception.SyntaxError,
        dns.resolver.NXDOMAIN,
        dns.resolver.NoAnswer,
    ):
        return []


def get_dns_record(
    domain: str,
    record_type: str,
    nameservers: List[str] = DEFAULT_NAMESERVERS,
) -> List[Tuple[str, str]]:
    """Get DNS record for a domain.

    Args:
        domain (str): Domain to get DNS record for.
        record_type (str): Record type to get.
        nameservers (list[str], optional): List of name servers to use.

    Raises:
        ValueError: If the record type is invalid.

    Returns:
        list[Tuple[str, str]]: List of DNS records.
    """
    record_type = record_type.upper()
    if is_valid_record_type(record_type) is False:
        raise ValueError(f"Invalid record type: {record_type}")

    # Configure DNS resolver with default name servers
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = nameservers
    resolver.search = []

    resolves = []

    if record_type == "PTR" and is_valid_ip_addr(domain) is True:
        resolves.extend(get_rdns_record(domain))
    else:
        try:
            # Retrieve DNS records for the domain
            records = resolver.resolve(domain, record_type)  # Example: A record
            for record in records:
                type_name = record.rdtype.name
                value = record.to_text()

                if type_name == "MX":
                    value = re.sub(r"(\s+?)?\d+(\s+?)?", "", value)
                    if value == ".":
                        continue

                resolves.append((type_name, value))
        except (
            dns.exception.SyntaxError,
            dns.resolver.NXDOMAIN,
            dns.resolver.NoAnswer,
        ):
            pass

    return resolves


def get_dns_records(
    domain: str, record_types: List[str] = DEFAULT_RECORD_TYPES
) -> List[List[Tuple[str, str]]]:
    """Get DNS records for a domain.

    Args:
        domain (str): Domain to get DNS records for.
        record_types (List[str], optional): List of record types to get.
            Defaults to DEFAULT_RECORD_TYPES.

    Returns:
        List[List[Tuple[str, str]]]: List of DNS records.
    """
    records = []
    for record_type in record_types:
        records.extend(get_dns_record(domain, record_type))

    return records
