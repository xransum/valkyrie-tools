"""Exception modules."""


REQUESTS_SSL_ERROR_MESSAGE = "SSL error."
REQUESTS_INVALID_URL_ERROR_MESSAGE = "Invalid URL."
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
REQUESTS_UNHANDLED_CONNECTION_ERROR_MESSAGE = "Unhandled connection failure."
REQUESTS_TIMEOUT_ERROR_MESSAGE = "Failed to connect, timeout reached."
REQUESTS_TOO_MANY_REDIRECTS_ERROR_MESSAGE = "Too many redirects."
