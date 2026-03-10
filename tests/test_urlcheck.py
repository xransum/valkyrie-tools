"""Urlcheck test module."""

import json
import unittest
from typing import List, Optional, Tuple, Union, cast
from unittest.mock import MagicMock, Mock, patch

import requests

from valkyrie_tools.constants import INTERACTIVE_MODE_PROMPT
from valkyrie_tools.exceptions import (
    REQUESTS_CONNECTION_ERROR_MESSAGES,
    REQUESTS_SSL_ERROR_MESSAGE,
    REQUESTS_TIMEOUT_ERROR_MESSAGE,
    REQUESTS_TOO_MANY_REDIRECTS_ERROR_MESSAGE,
    REQUESTS_UNHANDLED_CONNECTION_ERROR_MESSAGE,
)
from valkyrie_tools.urlcheck import (
    HEADER_KEY_TRUNC_LENGTH,
    _get_error_message,
    cli,
    json_extractor_urlcheck,
)

from .test_base_command import BaseCommandTest

META_HTML = (
    '<html><head><meta http-equiv="refresh" content="0; URL=%s"></head></html>'
)
LONG_HEADER_VALUE = "a" * (HEADER_KEY_TRUNC_LENGTH + 2)
URL_MOCKS = [
    ("http://example.com", 11, 200, "OK"),
    ("https://google.com/", 11, 200, "OK"),
    ("https://abc.123/", 11, 200, "OK"),
]
MOCK_REDIRECT_CHAIN = [
    ("http://example.com", 11, 301, "Moved Permanently"),
    ("http://www.example.com/", 11, 301, "Moved Permanently"),
    ("https://www.example.com/", 12, 302, "Found"),
    ("https://www.example.com/done", 12, 200, "OK"),
]


class TestURLCheckCLI(BaseCommandTest, unittest.TestCase):
    """Test suite for the valkyrie_tools.urlcheck command."""

    command = cli

    # @pytest.fixture(autouse=True)
    # def setup(self) -> None:
    #    """Init test case object."""
    #    self.runner = CliRunner()
    #    cli = cli

    def _create_mock_response(
        self,
        url: str,
        http_version: int,
        status_code: int,
        reason: str,
        next_url: Optional[str],
        redirects: bool = False,
        meta_redirect: bool = False,
    ) -> List[Union[str, Mock]]:
        """Create a mock response."""
        from requests import Response

        mock_response = Mock()
        mock_response.__class__ = Response  # type: ignore[assignment]  # noqa: B950
        mock_response.headers = {
            "Content-Type": "text/html",
            "Content-Length": "11",
            "Long-Header": LONG_HEADER_VALUE,
        }

        mock_response.status_code = status_code
        mock_response.reason = reason
        mock_response.raw.version = http_version
        mock_response.text = "Hello World!"

        if redirects is True:
            if next_url is not None:
                if meta_redirect is True:
                    mock_response.text = META_HTML % next_url
                else:
                    mock_response.headers.update({"Location": next_url})

        return [url, mock_response]

    def _create_mock_responses(
        self,
        response_chains: Union[
            List[Tuple[str, int, int, str]], Tuple[str, int, int, str]
        ],
        redirects: bool = False,
        meta_redirect: bool = False,
        max_next: Optional[int] = None,
    ) -> Union[List[List[Union[str, Mock]]], List[Union[str, Mock]]]:
        """Create mock responses from response chains."""
        single_chain = False
        if isinstance(response_chains, tuple):
            response_chains = [response_chains]
            single_chain = True

        mock_responses = []
        for c in range(len(response_chains)):
            chain = response_chains[c]
            url, http_version, status_code, reason = chain
            next_url = None

            if c < len(response_chains) - 1:
                next_url = response_chains[c + 1][0]

            mock_response = self._create_mock_response(
                url,
                http_version,
                status_code,
                reason,
                next_url,
                redirects,
                meta_redirect,
            )

            mock_responses.append(mock_response)
            # If it's the last chain, don't add another response, and
            # remove the Location header and text from the response.
            if max_next is not None and c >= max_next:
                cast(Mock, mock_response[1]).headers.pop("Location", None)
                cast(Mock, mock_response[1]).text = "Hello World!"
                break

        if single_chain is True:
            return mock_responses[0]

        return mock_responses

    def setUp(self) -> None:
        """Set up test fixtures, if any."""
        super().setUp()

    def tearDown(self) -> None:
        """Tear down test fixtures, if any."""
        super().tearDown()

    @patch("valkyrie_tools.httpr.make_request")
    def test_show_headers_option(self, mock_make_request: MagicMock) -> None:
        """Test --show-headers option."""
        mock_chain_link = self._create_mock_responses(URL_MOCKS[0])
        url = cast(str, mock_chain_link[0])
        mock_make_request.return_value = mock_chain_link
        result = self.runner.invoke(self.command, [url, "--show-headers"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("...", result.output)

    @patch("valkyrie_tools.httpr.make_request")
    def test_show_headers_no_truncate_option(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test --no-truncate option."""
        mock_chain_link = self._create_mock_responses(URL_MOCKS[0])
        url = cast(str, mock_chain_link[0])
        mock_make_request.return_value = mock_chain_link
        result = self.runner.invoke(
            self.command, [url, "--show-headers", "--no-truncate"]
        )

        self.assertNotIn("...", result.output)
        self.assertEqual(result.exit_code, 0)

    @patch("valkyrie_tools.httpr.make_request")
    def test_interactive_mode(self, mock_make_request: MagicMock) -> None:
        """Test interactive mode."""
        mock_chain_link = self._create_mock_responses(URL_MOCKS[0])
        url = cast(str, mock_chain_link[0])
        mock_make_request.return_value = mock_chain_link

        # Mock the sys.stdin read method to simulate user input.
        with patch("valkyrie_tools.commons.sys") as mock_sys:
            # Override isatty to simulate a terminal and simulate
            # user input.
            mock_sys.stdin.isatty.return_value = True
            mock_sys.stdin.read.side_effect = [
                url,
                "",  # Simulates CTRL+d
            ]

            result = self.runner.invoke(self.command, ["--interactive"])

        self.assertIn(INTERACTIVE_MODE_PROMPT, result.output)
        self.assertIn(url, result.output)
        self.assertEqual(result.exit_code, 0)

    # @patch("valkyrie_tools.httpr.make_request")
    # def test_output_file_option(self, mock_make_request: MagicMock) -> None:
    #     """Test --output-file option."""
    #     mock_chain_link = self._create_mock_responses(URL_MOCKS[0])
    #     url, mock_response = mock_chain_link
    #     mock_make_request.return_value = mock_chain_link

    #     with self.runner.isolated_filesystem():
    #         output_file = "output.txt"
    #         result = self.runner.invoke(self.command, [url, "-o", output_file])

    #         self.assertTrue(os.path.exists(output_file))
    #         self.assertEqual(result.exit_code, 0)

    @patch("valkyrie_tools.httpr.make_request")
    def test_single_url(self, mock_make_request: MagicMock) -> None:
        """Test single url."""
        mock_chain_link = self._create_mock_responses(URL_MOCKS[0])
        url = cast(str, mock_chain_link[0])
        mock_make_request.return_value = mock_chain_link
        result = self.runner.invoke(self.command, url)

        self.assertIn(url, result.output)
        self.assertEqual(result.exit_code, 0)

    @patch("valkyrie_tools.httpr.make_request")
    def test_single_url_piped(self, mock_make_request: MagicMock) -> None:
        """Test single piped url."""
        mock_chain_link = self._create_mock_responses(URL_MOCKS[0])
        url = cast(str, mock_chain_link[0])
        mock_make_request.return_value = mock_chain_link
        result = self.runner.invoke(self.command, input=url)

        self.assertIn(url, result.output)
        self.assertEqual(result.exit_code, 0)

    @patch("valkyrie_tools.httpr.make_request")
    def test_duplicate_urls(self, mock_make_request: MagicMock) -> None:
        """Test duplicate urls."""
        mock_chain_link = self._create_mock_responses(URL_MOCKS[0])
        url = cast(str, mock_chain_link[0])
        mock_make_request.return_value = mock_chain_link
        result = self.runner.invoke(self.command, f"{url} {url}")

        # Split lines and check only one url is in the output
        self.assertEqual(
            len([li for li in result.output.split("\n") if url in li]), 1
        )
        # self.assertEqual([True, True], [url in result.output for url in urls])
        self.assertEqual(result.exit_code, 0)

    @patch("valkyrie_tools.httpr.make_request")
    def test_multiple_urls(self, mock_make_request: MagicMock) -> None:
        """Test multiple non-duplicate urls."""
        mock_chain = self._create_mock_responses(URL_MOCKS[:2])
        mock_chain_a, mock_chain_b = mock_chain
        mock_make_request.side_effect = mock_chain
        urls = [mock_chain_a[0], mock_chain_b[0]]
        result = self.runner.invoke(self.command, " ".join(urls))

        self.assertEqual([True, True], [url in result.output for url in urls])
        self.assertEqual(result.exit_code, 0)

    @patch("valkyrie_tools.httpr.make_request")
    def test_redirect_chain_handling(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test redirect chain handling."""
        mock_chain = self._create_mock_responses(
            MOCK_REDIRECT_CHAIN, redirects=True
        )
        mock_chain_link = mock_chain[0]
        mock_make_request.side_effect = mock_chain
        result = self.runner.invoke(self.command, mock_chain_link[0])

        for url, _, _, _ in MOCK_REDIRECT_CHAIN:
            self.assertIn(url, result.output)

        self.assertEqual(result.exit_code, 0)

    @patch("valkyrie_tools.httpr.make_request")
    def test_request_ssl_exception(self, mock_make_request: MagicMock) -> None:
        """Test SSL exception."""
        url, *_ = URL_MOCKS[0]
        error = requests.exceptions.SSLError(REQUESTS_SSL_ERROR_MESSAGE)
        mock_make_request.return_value = [url, error]
        result = self.runner.invoke(self.command, url)
        self.assertIn(REQUESTS_SSL_ERROR_MESSAGE, result.output)

    @patch("valkyrie_tools.httpr.make_request")
    def test_request_connection_exceptions(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test connection exceptions."""
        url, *_ = URL_MOCKS[0]
        for key, value in REQUESTS_CONNECTION_ERROR_MESSAGES.items():
            error = requests.exceptions.ConnectionError(key)
            mock_make_request.return_value = [url, error]
            result = self.runner.invoke(self.command, url)
            self.assertIn(value, result.output)

    @patch("valkyrie_tools.httpr.make_request")
    def test_request_unhandled_connection_exception(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test unhandled connection exceptions."""
        url, *_ = URL_MOCKS[0]
        error = requests.exceptions.ConnectionError(
            "Unknown connection exception"
        )
        mock_make_request.return_value = [url, error]
        result = self.runner.invoke(self.command, url)
        print(result.output)
        self.assertIn(
            REQUESTS_UNHANDLED_CONNECTION_ERROR_MESSAGE, result.output
        )

    @patch("valkyrie_tools.httpr.make_request")
    def test_request_ambiguous_exception(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test ambiguous exception."""
        url, *_ = URL_MOCKS[0]
        msg = "Value exception."
        error = ValueError(msg)
        mock_make_request.return_value = [url, error]
        result = self.runner.invoke(self.command, url)
        print(result.output)
        self.assertIn(msg, result.output)

    @patch("valkyrie_tools.httpr.make_request")
    def test_request_timeout_exception(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test timeout exception."""
        url, *_ = URL_MOCKS[0]
        error = requests.exceptions.Timeout("Timeout exception thrown")
        mock_make_request.return_value = [url, error]
        result = self.runner.invoke(self.command, url)
        print(result.output)
        self.assertIn(REQUESTS_TIMEOUT_ERROR_MESSAGE, result.output)

    @patch("valkyrie_tools.httpr.make_request")
    def test_request_too_many_redirects_exception(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test too many redirects exception."""
        url, *_ = URL_MOCKS[0]
        error = requests.exceptions.TooManyRedirects(
            "Too many redirects thrown"
        )
        mock_make_request.return_value = [url, error]
        result = self.runner.invoke(self.command, url)
        print(result.output)
        self.assertIn(REQUESTS_TOO_MANY_REDIRECTS_ERROR_MESSAGE, result.output)

    @patch("valkyrie_tools.urlcheck.build_redirect_chain")
    def test_response_none_hop(
        self, mock_build_redirect_chain: MagicMock
    ) -> None:
        """Test hop with None response is silently skipped."""
        url, *_ = URL_MOCKS[0]
        mock_build_redirect_chain.return_value = [[url, None]]
        result = self.runner.invoke(self.command, url)
        self.assertEqual(result.exit_code, 0)

    @patch("valkyrie_tools.httpr.make_request")
    def test_request_status_codes(self, mock_make_request: MagicMock) -> None:
        """Test request status codes."""
        codes = [(c * 100 + ode) for c in range(1, 7) for ode in range(0, 10)]
        for code in codes:
            url, *_ = URL_MOCKS[0]
            mock_chain_link = self._create_mock_responses(
                (url, 11, code, "Status code %s" % code)
            )
            mock_make_request.return_value = mock_chain_link
            result = self.runner.invoke(self.command, url)
            self.assertIn(" - %i - " % code, result.output)


class TestUrlcheckJson(unittest.TestCase):
    """JSON output tests for urlcheck command."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        from click.testing import CliRunner

        self.runner = CliRunner()

    def _make_mock_response(
        self, url: str, status_code: int, reason: str, version: int = 11
    ) -> Mock:
        """Build a minimal mock requests.Response."""
        from requests import Response

        resp = Mock()
        resp.__class__ = Response  # type: ignore[assignment]
        resp.status_code = status_code
        resp.reason = reason
        resp.raw.version = version
        resp.headers = {}
        return resp

    @patch("valkyrie_tools.urlcheck.build_redirect_chain")
    def test_json_single_url(
        self, mock_build_redirect_chain: MagicMock
    ) -> None:
        """Test --json output for a single URL."""
        url = "http://example.com"
        resp = self._make_mock_response(url, 200, "OK")
        mock_build_redirect_chain.return_value = [[url, resp]]
        result = self.runner.invoke(cli, ["--json", url])
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertIsInstance(data, list)
        self.assertEqual(data[0]["input"], url)
        self.assertIn("chain", data[0])
        self.assertEqual(data[0]["chain"][0]["status_code"], 200)

    @patch("valkyrie_tools.urlcheck.build_redirect_chain")
    def test_json_exception_hop_becomes_error_entry(
        self, mock_build_redirect_chain: MagicMock
    ) -> None:
        """Test that an exception hop becomes an error dict in JSON mode."""
        url = "http://example.com"
        error = requests.exceptions.SSLError(REQUESTS_SSL_ERROR_MESSAGE)
        mock_build_redirect_chain.return_value = [[url, error]]
        result = self.runner.invoke(cli, ["--json", url])
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertIn("error", data[0]["chain"][0])

    @patch("valkyrie_tools.urlcheck.build_redirect_chain")
    def test_json_none_hop_produces_url_only_entry(
        self, mock_build_redirect_chain: MagicMock
    ) -> None:
        """Test that a None hop produces a bare url entry."""
        url = "http://example.com"
        mock_build_redirect_chain.return_value = [[url, None]]
        result = self.runner.invoke(cli, ["--json", url])
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertEqual(data[0]["chain"][0], {"url": url})

    @patch("valkyrie_tools.urlcheck.build_redirect_chain")
    def test_json_show_headers_flag(
        self, mock_build_redirect_chain: MagicMock
    ) -> None:
        """Test that --show-headers passes all headers in JSON mode."""
        url = "http://example.com"
        resp = self._make_mock_response(url, 200, "OK")
        resp.headers = {"X-Custom": "value", "Content-Type": "text/html"}
        mock_build_redirect_chain.return_value = [[url, resp]]
        result = self.runner.invoke(cli, ["--json", "--show-headers", url])
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        headers = data[0]["chain"][0]["headers"]
        self.assertIn("X-Custom", headers)

    @patch("valkyrie_tools.urlcheck.build_redirect_chain")
    def test_json_piped_input_extractor(
        self, mock_build_redirect_chain: MagicMock
    ) -> None:
        """Test that upstream JSON is parsed via extractor."""
        url = "http://example.com"
        resp = self._make_mock_response(url, 200, "OK")
        mock_build_redirect_chain.return_value = [[url, resp]]
        upstream = json.dumps([{"input": url}])
        result = self.runner.invoke(cli, ["--json"], input=upstream)
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertEqual(data[0]["input"], url)

    def test_json_piped_unrecognised_schema_raises(self) -> None:
        """Test that unrecognised piped JSON causes a non-zero exit."""
        upstream = json.dumps([{"foo": "bar"}])
        result = self.runner.invoke(cli, ["--json"], input=upstream)
        self.assertNotEqual(result.exit_code, 0)


class TestGetErrorMessage(unittest.TestCase):
    """Unit tests for _get_error_message helper."""

    def test_ssl_error(self) -> None:
        """Test SSLError maps to the SSL message."""
        err = requests.exceptions.SSLError("ssl")
        self.assertEqual(_get_error_message(err), REQUESTS_SSL_ERROR_MESSAGE)

    def test_timeout_error(self) -> None:
        """Test Timeout maps to the timeout message."""
        err = requests.exceptions.Timeout("timeout")
        self.assertEqual(
            _get_error_message(err), REQUESTS_TIMEOUT_ERROR_MESSAGE
        )

    def test_too_many_redirects_error(self) -> None:
        """Test TooManyRedirects maps to its message."""
        err = requests.exceptions.TooManyRedirects("redir")
        self.assertEqual(
            _get_error_message(err), REQUESTS_TOO_MANY_REDIRECTS_ERROR_MESSAGE
        )

    def test_connection_error_known(self) -> None:
        """Test a known ConnectionError pattern maps to its message."""
        first_key = next(iter(REQUESTS_CONNECTION_ERROR_MESSAGES))
        first_val = REQUESTS_CONNECTION_ERROR_MESSAGES[first_key]
        err = requests.exceptions.ConnectionError(first_key)
        self.assertEqual(_get_error_message(err), first_val)

    def test_connection_error_unknown(self) -> None:
        """Test an unknown ConnectionError maps to the unhandled message."""
        err = requests.exceptions.ConnectionError("totally unknown error text")
        self.assertEqual(
            _get_error_message(err),
            REQUESTS_UNHANDLED_CONNECTION_ERROR_MESSAGE,
        )

    def test_generic_exception(self) -> None:
        """Test a generic exception uses str()."""
        err = ValueError("some problem")
        self.assertEqual(_get_error_message(err), "some problem")


class TestJsonExtractorUrlcheck(unittest.TestCase):
    """Unit tests for json_extractor_urlcheck."""

    def test_extracts_input_fields(self) -> None:
        """Test that 'input' fields are extracted."""
        data = [{"input": "http://example.com"}, {"input": "http://other.com"}]
        result = json_extractor_urlcheck(data)
        self.assertEqual(result, ("http://example.com", "http://other.com"))

    def test_unrecognised_schema_raises(self) -> None:
        """Test that missing 'input' key raises ValueError."""
        with self.assertRaises(ValueError):
            json_extractor_urlcheck([{"chain": []}])

    def test_empty_list_returns_empty_tuple(self) -> None:
        """Test that an empty list returns an empty tuple."""
        result = json_extractor_urlcheck([])
        self.assertEqual(result, ())
