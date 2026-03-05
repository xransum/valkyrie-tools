"""Human-readable error message strings for HTTP request failures.

This module does **not** define exception classes; it only provides string
constants that are displayed to the user when :mod:`requests` raises an
exception during URL checking.  Each constant maps a specific
:mod:`requests.exceptions` type (or a substring of its error message) to a
concise, user-friendly description.
"""

REQUESTS_SSL_ERROR_MESSAGE = "SSL error."
"""Message shown when a :class:`requests.exceptions.SSLError` is caught."""

REQUESTS_INVALID_URL_ERROR_MESSAGE = "Invalid URL."
"""Message shown when a :class:`requests.exceptions.InvalidURL` is caught."""

REQUESTS_CONNECTION_ERROR_MESSAGES = {
    "Failed to resolve": "Failed to resolve host.",
    "Name or service not known": "Name or service not known.",
    "Temporary failure in name resolution": "Temporary failure in name resolution.",
    "nodename nor servname provided, or not known": (
        "Node name nor server name provided, or not known."
    ),
    "Connection refused": "Connection refused.",
    "Connection timed out": "Connection timed out.",
    "Connection reset by peer": "Connection reset by peer.",
    "Connection closed": "Connection closed.",
    "Connection aborted": "Connection aborted.",
    "Connection broken": "Connection broken.",
}
"""Mapping of :class:`requests.exceptions.ConnectionError` message substrings
to user-friendly error descriptions.

Keys are substrings searched (via :func:`re.search`) in the exception message;
values are the corresponding human-readable strings that are printed to stderr.
"""

REQUESTS_UNHANDLED_CONNECTION_ERROR_MESSAGE = "Unhandled connection failure."
"""Fallback message when no key in :data:`REQUESTS_CONNECTION_ERROR_MESSAGES`
matches the :class:`requests.exceptions.ConnectionError` message."""

REQUESTS_TIMEOUT_ERROR_MESSAGE = "Failed to connect, timeout reached."
"""Message shown when a :class:`requests.exceptions.Timeout` is caught."""

REQUESTS_TOO_MANY_REDIRECTS_ERROR_MESSAGE = "Too many redirects."
"""Message shown when a :class:`requests.exceptions.TooManyRedirects` is
caught."""
