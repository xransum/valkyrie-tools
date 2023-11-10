"""Constants modules."""


__all__ = [
    "HELP_SHORT_TEXT",
    "NO_ARGS_TEXT",
    "INVALID_ARG_TEXT",
    "INVALID_FLAG_TEXT",
    "BINARY_FILE_READ_ERROR",
    "YES_NO_PROMPT",
    "INTERACTIVE_MODE_PROMPT",
]

# Errors
HELP_SHORT_TEXT = "Try '%s --help' or '%s -h' for more information"
NO_ARGS_TEXT = "No arg(s) provided"
INVALID_ARG_TEXT = "Invalid %s"
INVALID_FLAG_TEXT = "Invalid flag %s"
BINARY_FILE_READ_ERROR = "Cannot read binary files"

# Prompts
YES_NO_PROMPT = "%s [y/N]: "
INTERACTIVE_MODE_PROMPT = (
    "Enter/paste your text and Ctrl-D (Cmd-D on Mac or Ctrl-Z on Windows) to save it."
)
EMPTY_ARGS_NOT_ALLOWED = "Input args cannot be empty."

DEFAULT_CATEGORIZED_HEADERS = {
    "AWS": {
        "Cloudfront": [
            # https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/adding-cloudfront-headers.html
            "X-Amz-Cf-Id",
            "X-Amz-Cf-Pop",
            "X-Amzn-Trace-Id",
            "X-Cache",
            "X-Cache-Hits",
            "X-Served-By",
            "X-Timer",
            "X-XSS-Protection",
        ],
        "API Gateway": [
            "x-amzn-RequestId",
            "x-amzn-ErrorType",
            "x-amz-apigw-id",
            "X-Amz-Cf-Id",
            "X-Amzn-Trace-Id",
            "x-amzn-Remapped-Date",
        ],
        # AWS ELB
        "ELB": [
            # https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/how-elastic-load-balancing-works.html#request-routing
            # https://medium.com/@lancers/amazon-api-gateway-explaining-http-proxy-in-http-api-3ea0afe6b03c#:%7E:text=RequestId%20and%20API%20Gateway%20emitted%20custom%20headers
            "X-Forwarded-For",
            "X-Forwarded-Proto",
            "X-Forwarded-Port",
        ],
        "S3": [
            # https://docs.aws.amazon.com/AmazonS3/latest/API/RESTCommonResponseHeaders.html
            "Server",
            "x-amz-delete-marker",
            "x-amz-id-2",
            "x-amz-request-id",
            "x-amz-server-side-encryption",
            "x-amz-version-id",
        ],
    },
    "Fastly": {
        # https://developer.fastly.com/reference/http/http-headers
        "Fastly": [
            "Fastly-Cachetype",
            "Fastly-Client",
            "Fastly-Client-IP",
            "Fastly-Cookie-Overflow",
            "Fastly-Debug",
            "Fastly-Debug-Digest",
            "Fastly-Debug-Path",
            "Fastly-Debug-TTL",
            "Fastly-FF",
            "Fastly-Force-Shield",
            "Fastly-IO-Error",
            "Fastly-IO-Info",
            "Fastly-IO-Warning",
            "Fastly-Key",
            "Fastly-No-Shield",
            "Fastly-SSL",
            "Fastly-Stats",
            "X-Fastly-Imageopto-API",
            "X-Fastly-Imageopto-Montage",
            "X-Fastly-Imageopto-Overlay",
        ],
    },
    "Cloudflare": {
        # https://developers.cloudflare.com/fundamentals/reference/http-request-headers/
        "Cloudflare": [
            "Accept-Encoding",
            "CF-Connecting-IP",
            "CF-Connecting-IP",
            "CF-Connecting-IPv6",
            "CF-EW-Via",
            "CF-Pseudo-IPv4",
            "True-Client-IP",
            "X-Forwarded-For",
            "X-Forwarded-Proto",
            "CF-RAY",
            "CF-IPCountry",
            "CF-Visitor",
            "CDN-Loop",
            "CF-Worker",
            "Connection",
        ],
    },
    "Akamai": {
        # https://developer.akamai.com/legacy/introduction/Client_Request_Headers.html
        "Akamai": [
            "Akamai-Origin-Hop",
            "X-Akamai-Request-ID",
            "X-Cache",
            "X-Cache-Remote",
            "X-Check-Cacheable",
            "X-True-Cache-Key",
            "X-Cache-Key",
            "X-Serial",
        ]
    },
}
