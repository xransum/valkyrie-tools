"""File module tests."""
import os
import sys
import tempfile
import unittest
from glob import glob
from typing import List
from unittest.mock import Mock, patch

from click.testing import CliRunner

from valkyrie_tools.files import (
    is_binary_file,
    is_file_descriptor,
    path_exists,
    read_file,
)


class TestPathExistsFunction(unittest.TestCase):
    """Test path exists function."""

    def setUp(self) -> None:
        """Setup fixtures."""
        # Create a binary file
        self.tmp_file = tempfile.NamedTemporaryFile(delete=False)
        self.tmp_file.write(b"Hello World!")
        self.tmp_file.close()

        self.tmp_directory = tempfile.TemporaryDirectory()
        self.tmp_directory_name = self.tmp_directory.name

    def tearDown(self) -> None:
        """Teardown fixtures."""
        os.unlink(self.tmp_file.name)
        os.rmdir(self.tmp_directory_name)

    def test_path_exists(self) -> None:
        """Test path_exists function with valid file."""
        self.assertTrue(path_exists(self.tmp_file.name))

    def test_path_not_exists(self) -> None:
        """Test path_exists with invalid file."""
        self.assertFalse(path_exists("nonexistent_file"))

    def test_exception_path_exists(self) -> None:
        """Test path_exists function with invalid argument."""
        self.assertFalse(path_exists({"foo": "bar"}))


class TestReadFileFunction(unittest.TestCase):
    """Test read file function."""

    def setUp(self) -> None:
        """Setup fixtures."""
        # Create a binary file
        self.tmp_file = tempfile.NamedTemporaryFile(delete=False)
        self.tmp_file.write(b"Hello World!")
        self.tmp_file.close()

        self.tmp_directory = tempfile.TemporaryDirectory()
        self.tmp_directory_name = self.tmp_directory.name

    def tearDown(self) -> None:
        """Teardown fixtures."""
        os.unlink(self.tmp_file.name)
        os.rmdir(self.tmp_directory_name)

    def test_read_file(self) -> None:
        """Test path_exists function with valid file."""
        self.assertIn("Hello World!", read_file(self.tmp_file.name))

    def test_read_non_exists_file(self) -> None:
        """Test path_exists with invalid file."""
        self.assertFalse(path_exists("nonexistent_file"))

    @patch("valkyrie_tools.files.os.path.exists")
    def test_read_file_exception(self, mock_path_exists: Mock) -> None:
        """Test path_exists function with invalid argument."""
        mock_path_exists.return_value = False
        # Expect an OSError
        with self.assertRaises(OSError):
            read_file("nonexistent_file")

        mock_path_exists.assert_called()

    @patch("valkyrie_tools.files.os.path.exists")
    @patch("valkyrie_tools.files.os.path.islink")
    @patch("valkyrie_tools.files.os.path.isfile")
    @patch("valkyrie_tools.files.os.path.isdir")
    def test_read_directory(
        self,
        mock_isdir: Mock,
        mock_isfile: Mock,
        mock_islink: Mock,
        mock_exists: Mock,
    ) -> None:
        """Test read_file function for a directory."""
        mock_exists.return_value = True
        mock_islink.return_value = False
        mock_isfile.return_value = False
        mock_isdir.return_value = True

        # Create a dir in tmp for testing
        with self.assertRaises(OSError):
            read_file(self.tmp_directory_name)

        mock_exists.assert_called()
        mock_islink.assert_called()
        mock_isfile.assert_called()
        mock_isdir.assert_called()

    @patch("valkyrie_tools.files.os.path.exists")
    @patch("valkyrie_tools.files.os.path.islink")
    @patch("valkyrie_tools.files.os.path.isfile")
    @patch("valkyrie_tools.files.os.path.isdir")
    def test_read_failover(
        self,
        mock_isdir: Mock,
        mock_isfile: Mock,
        mock_islink: Mock,
        mock_exists: Mock,
    ) -> None:
        """Test read_file function failover using a directory."""
        mock_exists.return_value = True
        mock_islink.return_value = False
        mock_isfile.return_value = False
        mock_isdir.return_value = False

        # Create a dir in tmp for testing
        with self.assertRaises(OSError):
            read_file(self.tmp_directory_name)

        mock_exists.assert_called()
        mock_islink.assert_called()
        mock_isfile.assert_called()
        mock_isdir.assert_called()


class TestBinaryFileFunction(unittest.TestCase):
    """Test binary file functions."""

    def setUp(self) -> None:
        """Setup fixtures."""
        # Create a binary file
        self.tmp_file = tempfile.NamedTemporaryFile(delete=False)
        self.tmp_file.write(b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09")
        self.tmp_file.close()

    def tearDown(self) -> None:
        """Teardown fixtures."""
        os.unlink(self.tmp_file.name)

    def test_valid_binary_file(self) -> None:
        """Test is_binary_file function."""
        self.assertTrue(is_binary_file(self.tmp_file.name))

    def test_invalid_binary_file_path(self) -> None:
        """Test is_binary_file function."""
        self.assertFalse(is_binary_file(__file__))

    def test_directory_path(self) -> None:
        """Test is_binary_file function."""
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            self.assertFalse(is_binary_file(tmp_dir_name))


class TestFileDescriptorFunction(unittest.TestCase):
    """Test file descriptor functions."""

    def setUp(self) -> None:
        """Setup fixtures."""
        self.stdout = os.fdopen(os.dup(1), "w")
        self.tmp_file = tempfile.NamedTemporaryFile(delete=False)
        self.tmp_file.write(b"Hello World!")
        self.tmp_file.close()
        self.runner = CliRunner()

    def tearDown(self) -> None:
        """Teardown fixtures."""
        os.unlink(self.tmp_file.name)

    @staticmethod
    def _get_file_descriptors() -> List[str]:
        """Get file descriptors."""
        # Get the filepath for the systems stdout file descriptor
        # this would be /dev/fd/1 on Linux and /proc/self/fd/1 on
        # MacOS. This might not work on Windows.
        paths = iter(glob("/**/fd/*"))
        return paths

    def test_valid_file_descriptor(self) -> None:
        """Test is_file_descriptor function."""
        self.assertTrue(is_file_descriptor(self.stdout.fileno()))

    def test_valid_file_descriptor_str(self) -> None:
        """Test is_file_descriptor with string name."""
        # Mock a file with fd identifier
        with self.runner.isolated_filesystem():
            # create the file with a fd directory name
            # and in int as the name
            file_path = os.path.join(os.getcwd(), "fd", "1")
            os.mkdir("fd")
            with open(file_path, "w") as fd:
                fd.write("Hello World!")

            if sys.platform == "win32":
                self.assertEqual(is_file_descriptor(file_path), None)

            else:
                self.assertTrue(is_file_descriptor(file_path))

    def test_invalid_file_descriptor(self) -> None:
        """Test is_file_descriptor function."""
        self.assertFalse(is_file_descriptor(__file__))

    def test_invalid_int_file_descriptor(self) -> None:
        """Test is_file_descriptor function."""
        self.assertFalse(is_file_descriptor(1337))

    def test_empty_file_descriptor_path(self) -> None:
        """Test is_file_descriptor function."""
        self.assertFalse(is_file_descriptor(""))

    def test_obj_file_descriptor_path(self) -> None:
        """Test is_file_descriptor function."""
        self.assertFalse(is_file_descriptor({"foo": "bar"}))

    @patch("valkyrie_tools.files.isinstance")
    def test_path_str_exception(self, mock_isinstance: Mock) -> None:
        """Test path_exists function with invalid argument."""
        mock_isinstance.side_effect = [False, True]
        self.assertFalse(is_file_descriptor(None))
        mock_isinstance.assert_called()
