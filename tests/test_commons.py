"""Commons module tests."""
import os
import unittest
from unittest.mock import MagicMock, Mock, patch

from art import text2art  # noqa: F401

from valkyrie_tools.commons import (
    DOMAIN_REGEX,
    EMAIL_ADDR_REGEX,
    IPV4_ADDR_REGEX,
    IPV6_ADDR_REGEX,
    URL_REGEX,
    handle_value_argument,
    read_value_from_input,
    sys_exit,
)
from valkyrie_tools.constants import INTERACTIVE_MODE_PROMPT


class TestRegex(unittest.TestCase):
    """Test regex."""

    def setUp(self: unittest.TestCase) -> None:
        """Set up test fixtures, if any."""
        pass

    def test_url_regex(self: unittest.TestCase) -> None:
        """Test url regex."""
        self.assertIsNotNone(URL_REGEX.match("https://www.google.com"))
        self.assertIsNone(URL_REGEX.match("not a url"))

    def test_domain_regex(self: unittest.TestCase) -> None:
        """Test domain regex."""
        self.assertIsNotNone(DOMAIN_REGEX.match("google.com"))
        self.assertIsNone(DOMAIN_REGEX.match("not a domain"))

    def test_email_addr_regex(self: unittest.TestCase) -> None:
        """Test email address regex."""
        self.assertIsNotNone(EMAIL_ADDR_REGEX.match("test@gmail.com"))
        self.assertIsNone(EMAIL_ADDR_REGEX.match("not an email"))

    def test_ipv4_addr_regex(self: unittest.TestCase) -> None:
        """Test ipv4 address regex."""
        self.assertIsNotNone(IPV4_ADDR_REGEX.match("192.168.1.1"))
        self.assertIsNone(IPV4_ADDR_REGEX.match("not an ip address"))

    def test_ipv6_addr_regex(self: unittest.TestCase) -> None:
        """Test ipv6 address regex."""
        self.assertIsNotNone(
            IPV6_ADDR_REGEX.match("2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        )
        self.assertIsNone(IPV6_ADDR_REGEX.match("not an ip address"))


class TestSysExit(unittest.TestCase):
    """Test sys_exit."""

    @patch("sys.exit")
    @patch("click.echo")
    def test_sys_exit(
        self: unittest.TestCase, mock_echo: Mock, mock_exit: Mock
    ) -> None:
        """Test sys_exit."""
        sys_exit("error", 1, True)
        mock_echo.assert_any_call("error", err=True)
        mock_echo.assert_any_call("Try '--help' for more information", err=True)
        mock_exit.assert_called_once_with(1)


class TestHandleValueArgument(unittest.TestCase):
    """Test handle_value_argument."""

    def test_input_file(self: unittest.TestCase) -> None:
        """Test input file."""
        with open("test.txt", "w") as f:
            f.write("test content")

        self.assertEqual(handle_value_argument("value", "test.txt"), "test content")
        os.remove("test.txt")

    def test_value_string(self: unittest.TestCase) -> None:
        """Test value string."""
        self.assertEqual(handle_value_argument("value", None), "value")

    def test_value_file(self: unittest.TestCase) -> None:
        """Test value file."""
        with open("test.txt", "w") as f:
            f.write("test content")

        self.assertEqual(handle_value_argument("test.txt", None), "test content")
        os.remove("test.txt")

    def test_value_list(self: unittest.TestCase) -> None:
        """Test value list."""
        self.assertEqual(
            handle_value_argument(["value1", "value2"], None),
            ["value1", "value2"],
        )

    def test_value_list_files(self: unittest.TestCase) -> None:
        """Test value list files."""
        with open("test1.txt", "w") as f:
            f.write("test content1")

        with open("test2.txt", "w") as f:
            f.write("test content2")

        self.assertEqual(
            handle_value_argument(["test1.txt", "test2.txt"], None),
            ["test content1", "test content2"],
        )

        os.remove("test1.txt")
        os.remove("test2.txt")

    def test_value_other(self: unittest.TestCase) -> None:
        """Test value other."""
        self.assertEqual(handle_value_argument(123, None), 123)


class TestReadValueFromInput(unittest.TestCase):
    """Test read_value_from_input."""

    @patch("sys.stdin", new_callable=MagicMock)
    @patch("click.echo")
    def test_interactive_mode(
        self: unittest.TestCase, mock_echo: Mock, mock_stdin: Mock
    ) -> None:
        """Test interactive mode."""
        mock_stdin.read.return_value = "test input"
        result = read_value_from_input(None, True)
        self.assertEqual(result, ["test input"])
        mock_echo.assert_called()
        mock_echo.assert_called_with(INTERACTIVE_MODE_PROMPT)

    # TODO: Need to figure out how to test "text2art" here.
    @patch("sys.stdin", new_callable=MagicMock)
    @patch("click.echo")
    def test_interactive_mode_with_name(
        self: unittest.TestCase, mock_echo: Mock, mock_stdin: Mock
    ) -> None:
        """Test interactive mode with name."""
        mock_stdin.read.return_value = "test input"
        result = read_value_from_input(None, True, name="test")
        self.assertEqual(result, ["test input"])
        mock_echo.assert_called()
        mock_echo.assert_called_with(INTERACTIVE_MODE_PROMPT)

    @patch("sys.stdin", new_callable=MagicMock)
    def test_non_interactive_mode(self: unittest.TestCase, mock_stdin: Mock) -> None:
        """Test non-interactive mode."""
        mock_stdin.isatty.return_value = False
        mock_stdin.read.return_value = "test input"
        result = read_value_from_input(None, False)
        self.assertEqual(result, ["test input"])

    @patch("sys.stdin", new_callable=MagicMock)
    def test_value_non_interactive_mode(
        self: unittest.TestCase, mock_stdin: Mock
    ) -> None:
        """Test value non-interactive mode."""
        mock_stdin.isatty.return_value = True
        mock_stdin.read.return_value = "test input"
        result = read_value_from_input("test value", False)
        self.assertEqual(result, ["test value"])

    @patch("sys.stdin", new_callable=MagicMock)
    def test_none_value(self: unittest.TestCase, mock_stdin: Mock) -> None:
        """Test none value."""
        mock_stdin.isatty.return_value = True
        result = read_value_from_input(None, False)
        self.assertEqual(result, [])

    @patch("sys.stdin", new_callable=MagicMock)
    def test_empty_value(self: unittest.TestCase, mock_stdin: Mock) -> None:
        """Test empty value."""
        mock_stdin.isatty.return_value = True
        result = read_value_from_input("", False)
        self.assertEqual(result, [""])

    @patch("sys.stdin", new_callable=MagicMock)
    def test_empty_list_value(self: unittest.TestCase, mock_stdin: Mock) -> None:
        """Test empty list value."""
        mock_stdin.isatty.return_value = True
        result = read_value_from_input([], False)
        self.assertEqual(result, [])

    @patch("sys.stdin", new_callable=MagicMock)
    def test_empty_tuple_value(self: unittest.TestCase, mock_stdin: Mock) -> None:
        """Test empty tuple value."""
        mock_stdin.isatty.return_value = True
        result = read_value_from_input((), False)
        self.assertEqual(result, [])

    @patch("sys.stdin", new_callable=MagicMock)
    def test_list_value(self: unittest.TestCase, mock_stdin: Mock) -> None:
        """Test list value."""
        mock_stdin.isatty.return_value = True
        result = read_value_from_input(["value1", "value2"], False)
        self.assertEqual(result, ["value1", "value2"])

    @patch("sys.stdin", new_callable=MagicMock)
    def test_string_value(self: unittest.TestCase, mock_stdin: Mock) -> None:
        """Test string value."""
        mock_stdin.isatty.return_value = True
        result = read_value_from_input("value", False)
        self.assertEqual(result, ["value"])

    @patch("sys.stdin", new_callable=MagicMock)
    def test_string_value_with_space(self: unittest.TestCase, mock_stdin: Mock) -> None:
        """Test string value with space."""
        mock_stdin.isatty.return_value = True
        result = read_value_from_input("value with space", False)
        self.assertEqual(result, ["value with space"])