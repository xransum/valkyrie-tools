"""Commons module tests."""

import unittest
from typing import Any, List, Tuple
from unittest.mock import MagicMock, patch

import click
from art import text2art  # type: ignore[import-untyped]  # noqa: F401
from click.testing import CliRunner

from valkyrie_tools.commons import (
    common_options,
    emit_json,
    extract_domains,
    extract_emails,
    extract_ip_addrs,
    extract_ipv4_addrs,
    extract_ipv6_addrs,
    extract_urls,
    handle_file_input,
    parse_input_methods,
    parse_json_stdin,
    print_version,
)


class TestCLI(unittest.TestCase):
    """Test cases for command line interface."""

    def setUp(self) -> None:
        """Set up testing environment."""
        self.runner = CliRunner()

    def test_common_options(self) -> None:
        """Test common_options decorator."""

        @common_options(
            cmd_type=click.command,
            name="test",
            description="Test command",
            version="1.0.0",
        )
        def test_command(values: Any, *_: Any, **__: Any) -> None:  # noqa: F811
            """A test command."""
            print(" ".join(values))

        result = self.runner.invoke(test_command, ["hello", "world"])
        # print(result.output)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.strip(), "hello world")

        # result = self.runner.invoke(test_command, ["--version"])
        # Should be non-zero, flags being deprecated for sub-cmds.
        # self.assertEqual(result.exit_code, 2)
        # self.assertEqual(result.output.strip(), "test 1.0.0")

    def test_print_version(self) -> None:
        """Test print_version function."""
        version_printer = print_version("1.0.0")

        class DummyContext:
            """Dummy context class."""

            resilient_parsing = False

            def exit(self) -> None:
                """Dummy exit method."""
                pass

        version_printer(DummyContext(), None, True)


class TestPrintVersion(unittest.TestCase):
    """Test suite for print_version function."""

    def test_valid_version_string(self) -> None:
        """Test that function returns a callable function."""
        version = "1.0.0"
        callback = print_version(version)
        self.assertTrue(callable(callback))

    def test_print_version_with_value(self) -> None:
        """Test that function prints version string and exits."""
        version = "1.0.0"
        callback = print_version(version)
        ctx = click.Context(click.Command("test"))
        param = click.Option(["--version"])
        value = "value"
        with self.assertRaises(click.exceptions.Exit):
            result = callback(ctx, param, value)
            self.assertIn(version, result)  # type: ignore[arg-type]

    def test_print_version_without_value(self) -> None:
        """Test that function does not print version string and exits."""
        version = "1.0.0"
        callback = print_version(version)
        ctx = click.Context(click.Command("test"))
        param = click.Option(["--version"])
        value = None
        result = callback(ctx, param, value)
        self.assertEqual(result, value)
        # with self.assertRaises(click.exceptions.Exit):
        #    result(ctx, param, value)

    def test_empty_version_string(self) -> None:
        """Test that function raises an exception."""
        version = ""
        with self.assertRaises(TypeError):
            callback = print_version(version)
            self.assertEqual(callback(), version)

    def test_print_version_with_no_param(self) -> None:
        """Test that function raises an exception."""
        version = "1.0.0"
        callback = print_version(version)
        ctx = click.Context(click.Command("test"))
        param = None
        value = "value"

        with self.assertRaises(click.exceptions.Exit):
            result = callback(ctx, param, value)
            self.assertEqual(result, version)


class TestHandleFileInput(unittest.TestCase):
    """Test suite for handle_file_input function."""

    def setUp(self) -> None:
        """Set up test fixtures, if any."""
        self.mock_context = click.Context(click.Command("test"))

    @patch("sys.stdin.isatty", return_value=True)
    @patch("os.path.exists", return_value=True)
    @patch("valkyrie_tools.commons.is_binary_file", return_value=False)
    @patch("os.path.isdir", return_value=False)
    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", new_callable=MagicMock)
    def test_file_input(self, mock_open: MagicMock, *_: Any) -> None:
        """Test that function reads from file if file path is provided."""
        mock_open.return_value.__enter__.return_value.read.return_value = (
            "file content"
        )
        result = handle_file_input("file_path")
        self.assertEqual(result, "file content")
        mock_open.assert_called_once_with("file_path", encoding="utf-8")

    @patch("sys.stdin.isatty", return_value=True)
    @patch("os.path.exists", return_value=True)
    @patch("valkyrie_tools.commons.is_binary_file", return_value=True)
    @patch("os.path.isdir", return_value=True)
    def test_binary_file_input(self, *_: Any) -> None:
        """Test that function reads from file if file path is provided."""
        # raise Exception
        with self.assertRaises(OSError):
            handle_file_input("file_path")

    @patch("sys.stdin.isatty", return_value=True)
    @patch("os.path.exists", return_value=True)
    @patch("valkyrie_tools.commons.is_binary_file", return_value=False)
    @patch("os.path.isdir", return_value=True)
    def test_directory_input(self, *_: Any) -> None:
        """Test that function reads from file if file path is provided."""
        # raise Exception
        with self.assertRaises(OSError):
            handle_file_input("dir_path")

    @patch("sys.stdin.isatty", return_value=True)
    @patch("os.path.exists", return_value=True)
    @patch("valkyrie_tools.commons.is_binary_file", return_value=False)
    @patch("os.path.isdir", return_value=False)
    @patch("os.path.isfile", return_value=False)
    def test_empty_arg(self, *_: Any) -> None:
        """Test that function handles invalid arg."""
        # raise Exception
        result = handle_file_input("null arg")
        self.assertEqual(None, result)


class TestParseInputMethods(unittest.TestCase):
    """Test parse_input_methods."""

    def setUp(self) -> None:
        """Set up test fixtures, if any."""
        self.mock_context = click.Context(click.Command("test"))

    @patch("sys.stdin", new_callable=MagicMock)
    @patch("click.echo", new_callable=MagicMock)
    def test_interactive_mode(
        self, mock_echo: MagicMock, mock_stdin: MagicMock
    ) -> None:
        """Test that function reads from stdin in interactive mode."""
        mock_stdin.read.return_value = "user input"
        result = parse_input_methods((), True, self.mock_context)
        self.assertEqual(result, ("user input",))
        mock_echo.assert_called()
        mock_stdin.read.assert_called_once()

    @patch("sys.stdin", new_callable=MagicMock)
    @patch("click.echo", new_callable=MagicMock)
    def test_interactive_mode_empty_stdin(
        self, mock_echo: MagicMock, mock_stdin: MagicMock
    ) -> None:
        """Test that function reads from stdin in interactive mode."""
        mock_stdin.read.return_value = ""
        result = parse_input_methods((), True, self.mock_context)
        self.assertEqual(result, ())
        mock_echo.assert_called()
        mock_stdin.read.assert_called_once()

    @patch("sys.stdin", new_callable=MagicMock)
    def test_non_interactive_mode(self, mock_stdin: MagicMock) -> None:
        """Test that function reads from stdin in non-interactive mode."""
        mock_stdin.isatty.return_value = False
        mock_stdin.read.return_value = "piped input"
        result = parse_input_methods(("-",), False, self.mock_context)
        self.assertEqual(result, ("piped input",))
        mock_stdin.read.assert_called_once()

    @patch("sys.stdin", new_callable=MagicMock)
    def test_non_interactive_mode_empty_args(
        self, mock_stdin: MagicMock
    ) -> None:
        """Test that function reads from stdin in non-interactive mode."""
        mock_stdin.isatty.return_value = False
        mock_stdin.read.return_value = "abc"
        result = parse_input_methods((), False, self.mock_context)
        self.assertEqual(result, ("abc",))
        mock_stdin.read.assert_called_once()

    @patch("valkyrie_tools.commons.is_binary_file", return_value=False)
    @patch("sys.stdin.isatty", return_value=True)
    def test_non_file_input(
        self,
        mock_is_binary_file: MagicMock,
        mock_isatty: MagicMock,
    ) -> None:
        """Test that function uses the value provided if it's not a file path."""
        result = parse_input_methods(
            ("non_file_path",), False, self.mock_context
        )
        self.assertEqual(result, ("non_file_path",))

    @patch("sys.stdin.isatty", return_value=True)
    @patch("os.path.exists", return_value=True)
    @patch("valkyrie_tools.commons.is_binary_file", return_value=False)
    @patch("os.path.isdir", return_value=False)
    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", new_callable=MagicMock)
    def test_file_input(
        self,
        mock_open: MagicMock,
        mock_isfile: MagicMock,
        mock_isdir: MagicMock,
        mock_is_binary_file: MagicMock,
        mock_exists: MagicMock,
        mock_isatty: MagicMock,
    ) -> None:
        """Test that function reads from file if file path is provided."""
        mock_open.return_value.__enter__.return_value.read.return_value = (
            "file content"
        )
        result = parse_input_methods(("file_path",), False, self.mock_context)
        self.assertEqual(result, ("file content",))
        mock_open.assert_called_once_with("file_path", encoding="utf-8")

    @patch("sys.stdin.isatty", return_value=True)
    @patch("os.path.exists", return_value=True)
    @patch("valkyrie_tools.commons.is_binary_file", return_value=True)
    @patch("os.path.isdir", return_value=True)
    def test_binary_file_input(
        self,
        mock_isdir: MagicMock,
        mock_is_binary_file: MagicMock,
        mock_exists: MagicMock,
        mock_isatty: MagicMock,
    ) -> None:
        """Test that function reads from file if file path is provided."""
        # raise Exception
        with self.assertRaises(OSError):
            parse_input_methods(("file_path",), False, self.mock_context)

    @patch("sys.stdin.isatty", return_value=True)
    @patch("os.path.exists", return_value=True)
    @patch("valkyrie_tools.commons.is_binary_file", return_value=False)
    @patch("os.path.isdir", return_value=True)
    def test_directory_input(
        self,
        mock_isdir: MagicMock,
        mock_is_binary_file: MagicMock,
        mock_exists: MagicMock,
        mock_isatty: MagicMock,
    ) -> None:
        """Test that function reads from file if file path is provided."""
        # raise Exception
        with self.assertRaises(OSError):
            parse_input_methods(("dir_path",), False, self.mock_context)

    @patch("sys.stdin.isatty", return_value=True)
    def test_multiple_args(self, mock_isatty: MagicMock) -> None:
        """Test that function reads from file if file path is provided."""
        result = parse_input_methods(
            ("arg1", "arg2", "arg3"), False, self.mock_context
        )
        self.assertEqual(result, ("arg1", "arg2", "arg3"))

    @patch("sys.stdin.isatty", return_value=True)
    def test_whitespace_arg(self, mock_isatty: MagicMock) -> None:
        """Test that function strips whitespaced args."""
        result = parse_input_methods(("     ",), False, self.mock_context)
        self.assertEqual(result, ("     ",))


class TestRegexExtraction(unittest.TestCase):
    """Test regex extraction functions."""

    def setUp(self) -> None:
        """Set up test fixtures, if any."""
        self.text = (
            "Test text with domain.com, 192.168.0.1, "
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334, test@domain.com, "
            "and http://domain.com"
        )

    def test_extract_domains(self) -> None:
        """Test extract_domains."""
        expected_result = ["domain.com"]
        self.assertEqual(
            extract_domains(self.text, unique=True), expected_result
        )

    def test_extract_ipv4_addrs(self) -> None:
        """Test extract_ipv4_addrs."""
        expected_result = ["192.168.0.1"]
        self.assertEqual(
            extract_ipv4_addrs(self.text, unique=True), expected_result
        )

    def test_extract_ipv6_addrs(self) -> None:
        """Test extract_ipv6_addrs."""
        expected_result = ["2001:0db8:85a3:0000:0000:8a2e:0370:7334"]
        self.assertEqual(
            extract_ipv6_addrs(self.text, unique=True), expected_result
        )

    def test_extract_ip_addrs(self) -> None:
        """Test extract_ip_addrs."""
        expected_result = [
            "192.168.0.1",
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
        ]
        self.assertEqual(
            extract_ip_addrs(self.text, unique=True), expected_result
        )

    def test_extract_emails(self) -> None:
        """Test extract_emails."""
        expected_result = ["test@domain.com"]
        self.assertEqual(
            extract_emails(self.text, unique=True), expected_result
        )

    def test_extract_urls(self) -> None:
        """Test extract_urls."""
        expected_result = ["http://domain.com"]
        self.assertEqual(extract_urls(self.text, unique=True), expected_result)


class TestEmitJson(unittest.TestCase):
    """Test suite for emit_json helper."""

    def test_emit_list(self) -> None:
        """Test that a list is serialised as a JSON array."""
        import json
        from io import StringIO
        from unittest.mock import patch

        buf = StringIO()
        with patch("click.echo", side_effect=lambda s: buf.write(s + "\n")):
            emit_json([{"input": "1.2.3.4", "foo": "bar"}])
        data = json.loads(buf.getvalue())
        self.assertIsInstance(data, list)
        self.assertEqual(data[0]["input"], "1.2.3.4")

    def test_emit_dict(self) -> None:
        """Test that a plain dict is serialised as a JSON object."""
        import json
        from io import StringIO
        from unittest.mock import patch

        buf = StringIO()
        with patch("click.echo", side_effect=lambda s: buf.write(s + "\n")):
            emit_json({"key": "foo", "updated": True})
        data = json.loads(buf.getvalue())
        self.assertIsInstance(data, dict)
        self.assertTrue(data["updated"])

    def test_emit_non_serialisable_falls_back_to_str(self) -> None:
        """Test that non-JSON-serialisable values are coerced to str."""
        import datetime
        import json
        from io import StringIO
        from unittest.mock import patch

        dt = datetime.datetime(2024, 1, 1)
        buf = StringIO()
        with patch("click.echo", side_effect=lambda s: buf.write(s + "\n")):
            emit_json({"ts": dt})
        data = json.loads(buf.getvalue())
        self.assertIsInstance(data["ts"], str)


class TestParseJsonStdin(unittest.TestCase):
    """Test suite for parse_json_stdin helper."""

    def _identity_extractor(self, data: List[Any]) -> Tuple[str, ...]:
        """Return input fields as a tuple."""
        return tuple(str(e["input"]) for e in data)

    def test_valid_json_array(self) -> None:
        """Test that a valid JSON array is decoded and extracted."""
        raw = '[{"input": "example.com"}]'
        result = parse_json_stdin(raw, self._identity_extractor)
        self.assertEqual(result, ("example.com",))

    def test_invalid_json_raises(self) -> None:
        """Test that invalid JSON raises UsageError."""
        import click

        with self.assertRaises(click.UsageError):
            parse_json_stdin("not json at all", self._identity_extractor)

    def test_non_array_json_raises(self) -> None:
        """Test that a JSON object (not array) raises UsageError."""
        import click

        with self.assertRaises(click.UsageError):
            parse_json_stdin('{"input": "x"}', self._identity_extractor)

    def test_extractor_value_error_raises_usage_error(self) -> None:
        """Test that a ValueError from the extractor is re-raised as UsageError."""
        import click

        def bad_extractor(data: List[Any]) -> Tuple[str, ...]:
            raise ValueError("unrecognised schema")

        with self.assertRaises(click.UsageError):
            parse_json_stdin('[{"foo": "bar"}]', bad_extractor)


class TestParseInputMethodsJsonMode(unittest.TestCase):
    """Tests for parse_input_methods JSON-piping path."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.ctx = click.Context(click.Command("test"))

    def _input_extractor(self, data: List[Any]) -> Tuple[str, ...]:
        return tuple(str(e["input"]) for e in data)

    @patch("sys.stdin", new_callable=MagicMock)
    def test_json_mode_pipes_through_extractor(
        self, mock_stdin: MagicMock
    ) -> None:
        """Piped JSON in --json mode is routed through the extractor."""
        mock_stdin.isatty.return_value = False
        mock_stdin.read.return_value = '[{"input": "1.2.3.4"}]'
        result = parse_input_methods(
            (),
            False,
            self.ctx,
            output_json=True,
            json_extractor=self._input_extractor,
        )
        self.assertEqual(result, ("1.2.3.4",))

    @patch("sys.stdin", new_callable=MagicMock)
    def test_json_mode_no_extractor_falls_back_to_plain(
        self, mock_stdin: MagicMock
    ) -> None:
        """Piped input in --json mode with no extractor is treated as plain text."""
        mock_stdin.isatty.return_value = False
        mock_stdin.read.return_value = "example.com"
        result = parse_input_methods(
            (),
            False,
            self.ctx,
            output_json=True,
            json_extractor=None,
        )
        self.assertEqual(result, ("example.com",))
