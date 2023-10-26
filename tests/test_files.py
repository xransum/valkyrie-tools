"""File module tests."""
import tempfile
import os

import pytest
from typing import Generator

from valkyrie_tools.files import (
    path_exists,
    is_binary_file,
    is_file_descriptor,
    read_file,
)


@pytest.fixture
def binary_file() -> Generator[str, None, None]:
    # Create a temporary binary file
    with tempfile.NamedTemporaryFile(delete=False) as file:
        file.write(b"\x00\x01\x02\x03")  # Write some binary data
        file.close()
        yield file.name

    # Clean up: delete the temporary binary file
    os.remove(file.name)


@pytest.fixture
def empty_file() -> Generator[str, None, None]:
    # Create a temporary empty file
    with tempfile.NamedTemporaryFile(delete=False) as file:
        yield file.name

    # Clean up: delete the temporary empty file
    os.remove(file.name)


def test_path_exists() -> None:
    """Check if the file is a regular file."""
    assert path_exists("non_existent_file") is False
    assert path_exists(__file__) is True


def test_is_binary_file(binary_file: str) -> None:
    """Check if the file is a binary file."""
    assert is_binary_file(__file__) is False
    assert is_binary_file(binary_file) is True


def test_is_file_descriptor(tmp_path: str) -> None:
    tmp_file = os.path.join(tmp_path, "test.txt")

    # Create a temporary file
    with open(tmp_file, "w") as f:
        f.write("test data")

    # Obtain the file descriptor
    file_descriptor = os.open(tmp_file, os.O_RDONLY)

    try:
        assert is_file_descriptor(file_descriptor) is True
    finally:
        # Close the file descriptor
        os.close(file_descriptor)


def test_read_file(empty_file: str) -> None:
    """Read the file content."""
    assert read_file(__file__) == open(__file__).read()
    assert read_file(empty_file) == ""
