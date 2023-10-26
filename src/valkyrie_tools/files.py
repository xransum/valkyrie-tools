"""File utilities."""
import os

__all__ = [
    "path_exists",
    "is_binary_file",
    "is_file_descriptor",
    "read_file",
]


def path_exists(file_path: str) -> bool:
    """Check if the file is a regular file."""
    try:
        return os.path.exists(file_path)
    except Exception:  # pragma: no cover
        return False


def is_binary_file(file_path: str) -> bool:
    """Check if the file is a binary file."""
    try:
        with open(file_path, "rb") as f:
            data = f.read(1024)  # Read the first 1024 bytes
        return any(byte < 9 or byte in (11, 12, 14, 15, 127) for byte in data)
    except OSError:  # pragma: no cover
        return False


def is_file_descriptor(file_path: int) -> bool:
    """Check if the file is a file descriptor."""
    try:
        return os.fstat(int(file_path)).st_dev == os.fstat(1).st_dev
    except (ValueError, FileNotFoundError):  # pragma: no cover
        return False


def read_file(file_path: str) -> str:
    """Read the file content."""
    try:
        with open(file_path) as f:
            return f.read()
    except OSError:  # pragma: no cover
        return ""  # Handle missing or inaccessible files gracefully
