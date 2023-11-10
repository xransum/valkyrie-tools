"""Httpr module for handling http requests and responses."""
import re
import warnings
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse, urlunparse  # noqa:F401

import requests
from bs4 import BeautifulSoup
from requests import Response
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress insecure request warnings
warnings.simplefilter("ignore", InsecureRequestWarning)


# Constants
NOW = datetime.now()
USER_AGENT_LIST = [
    (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/48.0.2564.116 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML,"
        " like Gecko) Version/13.1.1 Safari/605.1.15"
    ),
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/%s Firefox/77.0"
    % NOW.strftime("%Y%m%d"),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/83.0.4103.97 Safari/537.36"
    ),
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/%s Firefox/77.0"
    % NOW.strftime("%Y%m%d"),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like"
        " Gecko) Chrome/83.0.4103.97 Safari/537.36"
    ),
]
DEFAULT_USER_AGENT = USER_AGENT_LIST[0]
DEFAULT_REQUEST_HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "User-Agent": DEFAULT_USER_AGENT,
}
META_REDIRECT_REGEX = re.compile(
    "<meta[^>]*?url=(.*?)[\"']", re.IGNORECASE
)  # noqa: F841


def filter_headers(
    headers: Dict[str, str], keys: Optional[List[str]] = None
) -> Dict[str, str]:
    """Filter headers by key.

    Args:
        headers (Dict[str, str]): headers to filter
        keys (Optional[List[str]]): keys to filter by. Defaults to None.

    Returns:
        Dict[str, str]: filtered headers
    """
    if keys is None:
        keys = []

    filtered = {}
    if len(keys) > 0:
        for header, value in headers.items():
            for response_header in keys:
                if header.lower() == response_header.lower():
                    filtered[header] = value
    else:
        filtered = headers

    return filtered


def get_http_version(raw_version: int) -> str:
    """Given the raw.version, return the HTTP version as decimal string.

    Args:
        raw_version (int): raw version

    Returns:
        str: 1.0, 1.1, 1.2, 1.3, 2.0, etc.
    """
    splits = list(str(raw_version))
    splits.insert(1, ".")
    version = "".join(splits)
    return version


def get_http_version_text(raw_version: int) -> str:
    """Given the raw.version, return the HTTP version as decimal string.

    Args:
        raw_version (int): raw version

    Returns:
        str: HTTP/1.0, HTTP/1.1, HTTP/1.2, HTTP/1.3, etc.
    """
    tls_version = get_http_version(raw_version)
    return "HTTP/%s" % tls_version


def build_full_url(url: str, next_url: str) -> Optional[str]:
    """Builds a full URL from a relative URL.

    Args:
        url (str): url to build from
        next_url (str): relative url to build

    Returns:
        Optional[str]: full url
    """
    if next_url == "":
        return None

    uparsed = urlparse(url)
    if next_url.startswith("http"):
        return next_url
    elif next_url.startswith("//"):
        return uparsed.scheme + ":" + next_url
    elif next_url.startswith("/"):
        return uparsed.scheme + "://" + uparsed.netloc + next_url
    else:
        # TODO: Doesn't handle relative pathnames correctly
        return urljoin(url, next_url)


def extract_redirects_from_html_meta(soup: BeautifulSoup) -> Optional[str]:
    """Extracts HTML meta redirects from a BeautifulSoup object.

    Args:
        soup (BeautifulSoup): BeautifulSoup object

    Returns:
        Optional[str]: redirect url
    """
    meta_redirect = soup.find("meta", attrs={"http-equiv": "refresh"})
    if meta_redirect is not None:
        content = meta_redirect.get("content", "")
        if content != "":
            t = re.split(re.compile(r"url=", re.I), content)[1]
            t = re.sub(r'["\']', "", t).strip()
            return t

    return None


def make_request(
    method: str,
    url: str,
    **kwargs: Dict[str, Any],
) -> List[Union[str, Union[Response, Exception]]]:
    """Make a request to a given URL."""
    # The result will be a tuple of the URL and the response object,
    # or the URL and the error that's raised.
    try:
        with requests.request(method, url, **kwargs) as res:
            return [url, res]
    except Exception as e:
        # TODO: Handle this better
        return [url, e]


def get_next_url(res: Union[Response, Exception]) -> Optional[str]:
    """Get the next URL from a response.

    Args:
        res (Union[Response, Exception]): response object

    Returns:
        Optional[str]: next url
    """
    if isinstance(res, Exception):
        return None
    else:
        for key in res.headers.keys():
            if key.lower() == "location":
                return res.headers[key]

        else:
            return None


def build_redirect_chain(
    method: str,
    url: str,
    timeout: Optional[int] = 30,
    headers: Optional[Dict[str, str]] = None,
    proxies: Optional[Dict[str, str]] = None,
    follow_meta: bool = True,
    **kwargs: Dict[str, Any],
) -> List[Union[str, List[Union[str, Union[Response, Exception]]]]]:
    """Build a chain of HTTP redirects for a given URL."""
    chains = []
    current_url = url  # type: Optional[str]

    while current_url is not None:
        chain = [current_url, None]
        try:
            headers = {
                **DEFAULT_REQUEST_HEADERS,
                **(headers or {}),
            }
            chain = make_request(
                method,
                current_url,
                proxies=proxies,
                timeout=timeout,
                headers=headers,
                allow_redirects=False,
                verify=False,
                **kwargs,
            )
            res = chain[1]  # type: Union[Response, Exception]

            next_url = get_next_url(res)

            if next_url is None or next_url == "":
                if follow_meta is True:  # pragma: no cover
                    if isinstance(res, Exception) is False:
                        content_type = res.headers.get("Content-Type", "")

                        if "html" in content_type or "plain" in content_type:
                            content = res.text
                            soup = BeautifulSoup(content, "html.parser")
                            next_url = extract_redirects_from_html_meta(soup)

                            if next_url is not None:
                                current_url = build_full_url(current_url, next_url)
                            else:
                                current_url = None
                        else:
                            current_url = None
                    else:
                        current_url = None
                else:
                    current_url = None
            else:
                current_url = build_full_url(current_url, next_url)
        except Exception as e:
            chain[1] = e
            current_url = None

        chains.append(chain)

    return chains
