"""Test for valkyrie_tools.httpr module."""
import unittest
from typing import Any, Generator
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError

from valkyrie_tools.httpr import (
    DEFAULT_REQUEST_HEADERS,
    DEFAULT_USER_AGENT,
    USER_AGENT_LIST,
    build_full_url,
    build_redirect_chain,
    extract_redirects_from_html_meta,
    filter_headers,
    get_http_version,
    get_http_version_text,
    get_next_url,
    make_request,
)

META_REFRESH_HTML = (
    '<html><head><meta http-equiv="refresh" content="0;URL=\'%s\'" /> </head></html>'
)


class TestUserAgentList(unittest.TestCase):
    """Test for valkyrie_tools.httpr.USER_AGENT_LIST constant."""

    def test_user_agent_list(self: unittest.TestCase) -> None:
        """Test user agent list."""
        self.assertIsInstance(USER_AGENT_LIST, list)
        self.assertGreater(len(USER_AGENT_LIST), 0)
        for user_agent in USER_AGENT_LIST:
            self.assertIsInstance(user_agent, str)
            self.assertGreater(len(user_agent), 0)


class TestDefaultUserAgent(unittest.TestCase):
    """Test for valkyrie_tools.httpr.DEFAULT_USER_AGENT constant."""

    def test_default_user_agent(self: unittest.TestCase) -> None:
        """Test default user agent."""
        self.assertIsInstance(DEFAULT_USER_AGENT, str)
        self.assertGreater(len(DEFAULT_USER_AGENT), 0)


class TestDefaultRequestHeaders(unittest.TestCase):
    """Test for valkyrie_tools.httpr.DEFAULT_REQUEST_HEADERS constant."""

    def test_default_request_headers(self: unittest.TestCase) -> None:
        """Test default request headers."""
        self.assertIsInstance(DEFAULT_REQUEST_HEADERS, dict)
        self.assertGreater(len(DEFAULT_REQUEST_HEADERS), 0)
        for header_name, header_value in DEFAULT_REQUEST_HEADERS.items():
            self.assertIsInstance(header_name, str)
            self.assertIsInstance(header_value, str)
            self.assertGreater(len(header_name), 0)
            self.assertGreater(len(header_value), 0)


class TestFilterHeaders(unittest.TestCase):
    """Test for valkyrie_tools.httpr.filter_headers function."""

    def test_filter_headers_with_keys(self: unittest.TestCase) -> None:
        """Test filter headers with keys."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer token",
            "Cache-Control": "no-cache",
        }
        keys = ["content-type", "Cache-Control"]
        filtered = filter_headers(headers, keys)
        expected_result = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        }
        self.assertEqual(filtered, expected_result)

    def test_filter_headers_without_keys(self: unittest.TestCase) -> None:
        """Test filter headers without keys."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer token",
            "Cache-Control": "no-cache",
        }
        filtered = filter_headers(headers)
        self.assertEqual(filtered, headers)


class TestGetHttpVersion(unittest.TestCase):
    """Test for valkyrie_tools.httpr.get_http_version function."""

    def test_get_http_version(self: unittest.TestCase) -> None:
        """Test get http version."""
        # Test various raw versions and expected results
        test_cases = [
            (10, "1.0"),
            (11, "1.1"),
            (12, "1.2"),
            (13, "1.3"),
            (20, "2.0"),
            (35, "3.5"),
            (42, "4.2"),
        ]

        for raw_version, expected_result in test_cases:
            with self.subTest(raw_version=raw_version):
                result = get_http_version(raw_version)
                self.assertEqual(result, expected_result)


class TestGetHTTPVersionText(unittest.TestCase):
    """Test for valkyrie_tools.httpr.get_http_version_text function."""

    def test_get_http_version_text(self: unittest.TestCase) -> None:
        """Test get http version text."""
        test_cases = [
            (10, "HTTP/1.0"),
            (11, "HTTP/1.1"),
            (12, "HTTP/1.2"),
            (13, "HTTP/1.3"),
            (20, "HTTP/2.0"),
            (35, "HTTP/3.5"),
            (42, "HTTP/4.2"),
        ]

        for raw_version, expected_result in test_cases:
            with self.subTest(raw_version=raw_version):
                result = get_http_version_text(raw_version)
                self.assertEqual(result, expected_result)


class TestBuildFullURL(unittest.TestCase):
    """Tests for valkyrie_tools.httpr.build_full_url function."""

    def test_empty_relative_url(self: unittest.TestCase) -> None:
        """Test empty relative url."""
        base_url = "https://example.com"
        relative_url = ""
        result = build_full_url(base_url, relative_url)
        self.assertIsNone(result)

    def test_absolute_http_url(self: unittest.TestCase) -> None:
        """Test absolute http url."""
        base_url = "https://example.com"
        relative_url = "http://another.com"
        result = build_full_url(base_url, relative_url)
        self.assertEqual(result, "http://another.com")

    def test_scheme_relative_url(self: unittest.TestCase) -> None:
        """Test scheme relative url."""
        base_url = "https://example.com"
        relative_url = "//cdn.example.com/assets/style.css"
        result = build_full_url(base_url, relative_url)
        self.assertEqual(result, "https://cdn.example.com/assets/style.css")

    def test_path_relative_url(self: unittest.TestCase) -> None:
        """Test path relative url."""
        base_url = "https://example.com/page/"
        relative_url = "/about"
        result = build_full_url(base_url, relative_url)
        self.assertEqual(result, "https://example.com/about")

    def test_relative_url(self: unittest.TestCase) -> None:
        """Test relative url."""
        base_url = "https://example.com/page/"
        relative_url = "image.jpg"
        result = build_full_url(base_url, relative_url)
        self.assertEqual(result, "https://example.com/page/image.jpg")

    def test_invalid_relative_url(self: unittest.TestCase) -> None:
        """Test invalid relative url."""
        base_url = "https://example.com"
        relative_url = "javascript:alert('XSS')"
        result = build_full_url(base_url, relative_url)
        # TODO: Should this be None?
        self.assertEqual(result, "javascript:alert('XSS')")


class TestExtractRedirectsFromHTMLMeta(unittest.TestCase):
    """Tests for valkyrie_tools.httpr.extract_redirects_from_html_meta."""

    def test_no_meta_refresh_tag(self: unittest.TestCase) -> None:
        """Test no meta refresh tag."""
        html = "<html><head></head><body><p>Some content</p></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        result = extract_redirects_from_html_meta(soup)
        self.assertIsNone(result)

    def test_valid_meta_refresh_tag(self: unittest.TestCase) -> None:
        """Test valid meta refresh tag."""
        html = (
            '<html><head><meta http-equiv="refresh" content="5;'
            + 'url=https://example.com"></head></html>'
        )
        soup = BeautifulSoup(html, "html.parser")
        result = extract_redirects_from_html_meta(soup)
        self.assertEqual(result, "https://example.com")

    def test_invalid_meta_refresh_tag(self: unittest.TestCase) -> None:
        """Test invalid meta refresh tag."""
        html = (
            '<html><head><meta http-equiv="refresh" content="5;'
            + 'url=invalid-url"></head></html>'
        )
        soup = BeautifulSoup(html, "html.parser")
        result = extract_redirects_from_html_meta(soup)
        self.assertEqual(result, "invalid-url")

    def test_invalid_empty_meta_refresh_tag(self: unittest.TestCase) -> None:
        """Test invalid empty meta refresh tag."""
        html = (
            '<html><head><meta http-equiv="refresh" '
            + 'content="5;url="></head></html>'
        )
        soup = BeautifulSoup(html, "html.parser")
        result = extract_redirects_from_html_meta(soup)
        self.assertEqual(result, "")

    def test_invalid_meta_refresh_empty_content(
        self: unittest.TestCase,
    ) -> None:
        """Test invalid empty meta refresh content."""
        html = '<html><head><meta http-equiv="refresh" content=""></head></html>'
        soup = BeautifulSoup(html, "html.parser")
        result = extract_redirects_from_html_meta(soup)
        self.assertEqual(result, None)

    def test_invalid_meta_refresh_no_content(self: unittest.TestCase) -> None:
        """Test invalid empty meta refresh tag."""
        html = '<html><head><meta http-equiv="refresh"></head></html>'
        soup = BeautifulSoup(html, "html.parser")
        result = extract_redirects_from_html_meta(soup)
        self.assertEqual(result, None)


class TestGetNextUrl(unittest.TestCase):
    """Test for valkyrie_tools.httpr.get_next_url function."""

    def setUp(self: unittest.TestCase) -> None:
        """Set up the mock response object."""
        self.mock_response = Mock()
        self.mock_response.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer token",
            "Cache-Control": "no-cache",
        }
        self.mock_response.text = "Hello World!"

    def tearDown(self: unittest.TestCase) -> None:
        """Reset the mock response object."""
        self.mock_response = None

    def test_successful_get_next_url(
        self: unittest.TestCase,
    ) -> None:
        """Test get_next_url with a successful request."""
        url = "https://example.com"
        self.mock_response.headers["Location"] = url
        result = get_next_url(self.mock_response)
        self.assertEqual(result, url)

    def test_successful_get_next_url_alt_key(
        self: unittest.TestCase,
    ) -> None:
        """Test get_next_url with a successful request."""
        url = "https://example.com"
        self.mock_response.headers["location"] = url
        result = get_next_url(self.mock_response)
        self.assertEqual(result, url)

    def test_failed_get_next_url(
        self: unittest.TestCase,
    ) -> None:
        """Test get_next_url with a failed request."""
        result = get_next_url(self.mock_response)
        self.assertIsNone(result)

    def test_failed_get_next_url_with_exception(
        self: unittest.TestCase,
    ) -> None:
        """Test get_next_url with a failed request."""
        self.mock_response = Exception("Failed to make a request")
        result = get_next_url(self.mock_response)
        self.assertIsNone(result)


class TestMakeRequest(unittest.TestCase):
    """Test for valkyrie_tools.httpr.make_request function."""

    @patch("valkyrie_tools.httpr.requests.request")
    def test_successful_request(self: unittest.TestCase, mock_request: Mock) -> None:
        """Test make_request with a successful request."""
        url = "https://example.com"
        method = "GET"
        response_data = "Response data"

        # Create a mock response object
        mock_response = Mock()
        mock_response.text = response_data
        mock_request.return_value.__enter__.return_value = mock_response

        result = make_request(method, url)

        self.assertEqual(result[0], url)
        self.assertEqual(result[1].text, response_data)  # type: ignore

    @patch("valkyrie_tools.httpr.requests.request")
    def test_failed_request(self: unittest.TestCase, mock_request: Mock) -> None:
        """Test make_request with a failed request."""
        url = "https://example.com"
        method = "GET"
        error_message = "Failed to make a request"
        mock_request.side_effect = Exception(error_message)

        result = make_request(method, url)

        self.assertEqual(result[0], url)
        self.assertIsInstance(result[1], Exception)
        self.assertEqual(str(result[1]), error_message)


class TestBuildRedirectChain(unittest.TestCase):
    """Test for valkyrie_tools.httpr.build_redirect_chain function."""

    @patch("valkyrie_tools.httpr.make_request")
    def test_successful_redirect_chain(
        self: unittest.TestCase, mock_make_request: Mock
    ) -> None:
        """Test build_redirect_chain with a successful redirect chain."""
        url_chain = [
            "http://example.com",
            "http://www.example.com/",
            "https://www.example.com/",
            "https://www.example.com/done",
        ]

        def side_effect() -> Generator[Any, None, None]:
            print("side_effect")
            for u in range(len(url_chain)):
                url = url_chain[u]
                mock_response = Mock()
                mock_response.headers = {}
                mock_response.text = "x%i Hello World!" % u

                if u < len(url_chain) - 1:
                    mock_response.headers["Location"] = url_chain[u + 1]

                yield [url, mock_response]

        # Set up the side_effect to use the generator
        mock_make_request.side_effect = side_effect()

        # result = build_redirect_chain(
        #    method, url_chain[0], timeout, headers, proxies, follow_meta, **kwargs
        # )
        result = build_redirect_chain("GET", url_chain[0])
        self.assertEqual(len(url_chain), len(result))
        for u in range(len(url_chain)):
            url = url_chain[u]
            next_url = None
            if u < len(url_chain) - 1:
                next_url = url_chain[u + 1]

            mock_url, mock_res = result[u]
            self.assertEqual(url, mock_url)
            self.assertEqual(next_url, mock_res.headers.get("Location", None))  # type: ignore

    @patch("valkyrie_tools.httpr.make_request")
    def test_failed_redirect_chain(
        self: unittest.TestCase, mock_make_request: Mock
    ) -> None:
        """Test build_redirect_chain with a failed redirect chain."""
        url = "https://example.com"
        # Mock the make_request function to simulate a failure
        error_message = "Failed to make a request"
        mock_make_request.side_effect = [Exception(error_message)]

        result = build_redirect_chain(
            "GET",
            url,
            timeout=30,
            headers={"User-Agent": "Test"},
            follow_meta=True,
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], url)
        self.assertIsInstance(result[0][1], Exception)
        self.assertEqual(str(result[0][1]), error_message)

    @patch("valkyrie_tools.httpr.make_request")
    def test_successful_redirect_chain_with_empty_next_url(
        self: unittest.TestCase, mock_make_request: Mock
    ) -> None:
        """Test build_redirect_chain with an empty next URL."""
        url = "https://example.com"
        mock_response = Mock()
        mock_response.headers = {
            "Location": "",
        }
        mock_response.text = "Hello World!"

        mock_make_request.side_effect = [[url, mock_response]]
        result = build_redirect_chain("GET", url, follow_meta=False)
        self.assertEqual(len(result), 1)
        self.assertIn(url, [r[0] for r in result])

    @patch("valkyrie_tools.httpr.make_request")
    def test_successful_redirect_chain_with_empty_next_url_meta_false(
        self: unittest.TestCase, mock_make_request: Mock
    ) -> None:
        """Test build_redirect_chain with an empty next URL."""
        url = "https://example.com"
        mock_response = Mock()
        mock_response.headers = {}
        mock_response.text = "Hello World!"

        mock_make_request.side_effect = [[url, mock_response]]
        result = build_redirect_chain("GET", url, follow_meta=False)
        self.assertEqual(len(result), 1)
        self.assertIn(url, [r[0] for r in result])

    @patch("valkyrie_tools.httpr.make_request")
    def test_redirect_chain_with_follow_meta_false(
        self: unittest.TestCase, mock_make_request: Mock
    ) -> None:
        """Test build_redirect_chain with follow_meta=False."""
        url = "https://example.com"

        # Mock the make_request function to simulate a failure
        error_message = "Failed to make a request"
        mock_make_request.side_effect = [Exception(error_message)]

        result = build_redirect_chain("GET", url, follow_meta=False)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], url)

    @patch("valkyrie_tools.httpr.make_request")
    def test_redirect_chain_with_follow_meta_true_no_meta_refresh_tag(
        self: unittest.TestCase, mock_make_request: Mock
    ) -> None:
        """Test redirects with follow_meta=True and no meta refresh tag."""
        url = "https://example.com"
        mock_response = Mock()
        mock_response.headers = {}
        mock_make_request.side_effect = [[url, mock_response]]

        result = build_redirect_chain("GET", url, follow_meta=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], url)
        self.assertEqual(result[0][1], mock_response)

    @patch("valkyrie_tools.httpr.make_request")
    def test_redirect_chain_with_follow_meta_true_valid_meta_refresh_tag(
        self: unittest.TestCase, mock_make_request: Mock
    ) -> None:
        """Test redirects with follow_meta=True and valid meta refresh tag."""
        url_chain = [
            "https://example.com",
            "https://example.com/redirect",
        ]

        def side_effect() -> Generator[Any, None, None]:
            for i in range(len(url_chain)):
                url = url_chain[i]
                mock_response = Mock()
                mock_response.headers = {}
                mock_response.text = "Hello World!"
                if i < len(url_chain) - 1:
                    mock_response.headers["Content-Type"] = "text/html"
                    mock_response.text = META_REFRESH_HTML % url_chain[i + 1]

                yield [url, mock_response]

        mock_make_request.side_effect = side_effect()

        result = build_redirect_chain("GET", url_chain[0], follow_meta=True)
        self.assertEqual(len(result), len(url_chain))

        for u in range(len(url_chain)):
            url = url_chain[u]
            next_url = None
            if u < len(url_chain) - 1:
                next_url = url_chain[u + 1]

            mock_url, mock_res = result[u]
            self.assertEqual(url, mock_url)

            # TODO: No entirely the best way to test this
            if next_url is not None:
                self.assertIn(next_url, mock_res.text)

    @patch("valkyrie_tools.httpr.make_request")
    def test_redirect_chain_with_text_content_type(
        self: unittest.TestCase, mock_make_request: Mock
    ) -> None:
        """Test build_redirect_chain with text content type."""
        url = "https://example.com"
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.text = "Hello World!"
        mock_make_request.side_effect = [[url, mock_response]]

        result = build_redirect_chain("GET", url)
        print(result)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], url)
        self.assertEqual(result[0][1], mock_response)

    @patch("valkyrie_tools.httpr.make_request")
    def test_redirect_chain_with_non_html_content_type(
        self: unittest.TestCase, mock_make_request: Mock
    ) -> None:
        """Test build_redirect_chain with non-HTML content type."""
        url = "https://example.com"
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_make_request.side_effect = [[url, mock_response]]

        result = build_redirect_chain("GET", url, follow_meta=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], url)
        self.assertEqual(result[0][1], mock_response)

    @patch("valkyrie_tools.httpr.make_request")
    def test_redirect_chain_with_dns_resolution_failure(
        self: unittest.TestCase, mock_make_request: Mock
    ) -> None:
        """Test build_redirect_chain with DNS resolution failure."""
        url = "https://example.com"
        mock_make_request.side_effect = [[url, ConnectionError("Failed to resolve")]]

        result = build_redirect_chain("GET", url)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], url)
        self.assertIsInstance(result[0][1], ConnectionError)
        self.assertEqual(str(result[0][1]), "Failed to resolve")
