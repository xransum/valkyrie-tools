"""Httpr module for handling http requests and responses."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, cast
from urllib.parse import urljoin, urlparse, urlunparse  # noqa:F401

import requests
import urllib3
from bs4 import BeautifulSoup
from bs4.element import Tag
from requests import Response

# Suppress insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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

    Resolves ``next_url`` against ``url`` using the following rules:

    - Empty ``next_url`` -> ``None``.
    - ``next_url`` starting with ``http`` -> returned unchanged.
    - ``next_url`` starting with ``//`` -> scheme from ``url`` is prepended.
    - ``next_url`` starting with ``/`` -> scheme + netloc from ``url`` is
      prepended.
    - Otherwise -> :func:`urllib.parse.urljoin` is used.  Note: relative
      path segments (e.g. ``"../other"``) may not resolve correctly in all
      cases.

    Args:
        url (str): The base URL whose scheme/netloc is used for resolution.
        next_url (str): The relative or absolute URL to resolve.

    Returns:
        Optional[str]: The resolved absolute URL, or ``None`` if
        ``next_url`` is an empty string.

    Example:
        >>> from valkyrie_tools.httpr import build_full_url
        >>> build_full_url("https://example.com/page", "/other")
        'https://example.com/other'
        >>> build_full_url("https://example.com/page", "//cdn.example.com/img.png")
        'https://cdn.example.com/img.png'
        >>> build_full_url("https://example.com/page", "") is None
        True
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
    if meta_redirect is not None and isinstance(meta_redirect, Tag):
        raw_content = meta_redirect.get("content", "")
        # .get() on a Tag returns _AttributeValue; cast to str for re operations
        content = str(raw_content) if raw_content is not None else ""
        if content != "":
            t = re.split(re.compile(r"url=", re.I), content)[1]
            t = re.sub(r'["\']', "", t).strip()
            return t

    return None


def make_request(
    method: str,
    url: str,
    **kwargs: Any,
) -> List[Union[str, Union[Response, Exception]]]:
    """Make a single HTTP request and return the URL paired with the response.

    Wraps :func:`requests.request` with ``allow_redirects=False`` semantics
    (callers control redirect following manually).  Any exception raised by
    ``requests`` is caught and returned as the second element of the result
    list instead of being re-raised, so callers should check whether the
    second element is an :class:`Exception` subclass before accessing
    response attributes.

    Args:
        method (str): HTTP method (e.g. ``"GET"``, ``"POST"``).
        url (str): The URL to request.
        **kwargs: Additional keyword arguments forwarded directly to
            :func:`requests.request` (e.g. ``headers``, ``timeout``,
            ``proxies``, ``verify``).

    Returns:
        List[Union[str, Union[Response, Exception]]]: A two-element list
        ``[url, result]`` where ``result`` is either a
        :class:`requests.Response` on success or the caught
        :class:`Exception` on failure.
    """
    # The result will be a tuple of the URL and the response object,
    # or the URL and the error that's raised.
    try:
        with requests.request(method, url, **kwargs) as res:
            return [url, res]
    except Exception as e:
        # TODO: Handle this better
        return [url, e]


def get_next_url(res: Union[Response, Exception]) -> Optional[str]:
    """Extract the next URL from an HTTP response's ``Location`` header.

    Args:
        res (Union[Response, Exception]): The response object from a previous
            request, or an :class:`Exception` if the request failed.

    Returns:
        Optional[str]: The value of the ``Location`` header if present, or
        ``None`` if ``res`` is an :class:`Exception` or no ``Location``
        header exists.  Note that ``None`` is returned in both cases; callers
        cannot distinguish between a network failure and a response with no
        redirect header.
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
    **kwargs: Any,
) -> List[Union[str, List[Union[str, Union[Response, Exception]]]]]:
    """Build the full HTTP redirect chain for a given URL.

    Follows ``Location`` header redirects (and optionally HTML ``<meta
    http-equiv="refresh">`` redirects) one hop at a time until no further
    redirect is detected or an exception terminates the chain.  Each hop is
    collected as a two-element ``[url, response_or_exception]`` list.

    Args:
        method (str): HTTP method to use for every request in the chain
            (e.g. ``"GET"``).
        url (str): The initial URL to start the chain from.
        timeout (Optional[int]): Request timeout in seconds applied to every
            hop.  Defaults to ``30``.
        headers (Optional[Dict[str, str]]): Extra request headers merged on
            top of :data:`DEFAULT_REQUEST_HEADERS` for every hop.  Defaults
            to ``None`` (only default headers are used).
        proxies (Optional[Dict[str, str]]): Proxy map forwarded to
            :func:`requests.request`.  Defaults to ``None``.
        follow_meta (bool): When ``True``, also follow HTML meta
            ``http-equiv="refresh"`` redirects when no ``Location`` header is
            present.  Defaults to ``True``.
        **kwargs: Additional keyword arguments forwarded to
            :func:`make_request` (and on to :func:`requests.request`).

    Returns:
        List[Union[str, List[Union[str, Union[Response, Exception]]]]]:
        An ordered list of hops.  Each hop is a two-element list
        ``[url, result]`` where ``result`` is a :class:`requests.Response`
        on success or an :class:`Exception` on failure.  The list contains
        at least one entry (the initial URL).
    """
    chains = []  # type: List[Any]
    current_url = url  # type: Optional[str]

    while current_url is not None:
        chain = [current_url, None]  # type: List[Any]
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
            res = cast(Union[Response, Exception], chain[1])

            next_url = get_next_url(res)

            if next_url is None or next_url == "":
                if follow_meta is True:  # pragma: no cover
                    if not isinstance(res, Exception):
                        content_type = res.headers.get("Content-Type", "")

                        if "html" in content_type or "plain" in content_type:
                            content = res.text
                            soup = BeautifulSoup(content, "html.parser")
                            next_url = extract_redirects_from_html_meta(soup)

                            if next_url is not None:
                                current_url = build_full_url(
                                    current_url, next_url
                                )
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
