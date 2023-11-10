"""File utilities."""
import os
from typing import Optional, Union

__all__ = [
    "path_exists",
    "is_binary_file",
    "is_file_descriptor",
    "read_file",
]


def path_exists(path: str) -> bool:
    """Check if the file is a regular file.

    Args:
        path (str): File path.

    Returns:
        bool: True if path is a regular file.
    """
    try:
        return os.path.exists(path)
    except Exception:  # pragma: no cover
        return False


def is_binary_file(path: str) -> bool:
    """Check if the file is a binary file.

    Args:
        path (str): File path.

    Returns:
        bool: True if path is a binary file.
    """
    try:
        with open(path, "rb") as f:
            # Read the first 1024 bytes
            data = f.read(1024)

        return any(byte < 9 or byte in (11, 12, 14, 15, 127) for byte in data)
    except OSError:  # pragma: no cover
        return False


def is_file_descriptor(path: Union[str, int]) -> bool:
    """Check if arg is a file descriptor.

    Args:
        path (Union[str, int]): File path or file descriptor.

    Returns:
        bool: True if path is a file descriptor.
    """
    if isinstance(path, int):
        try:
            os.fstat(path)
            return True
        except Exception:
            return False
    elif isinstance(path, str):
        try:
            # On Linux, /dev/fd/x is a symlink to /proc/self/fd/x and
            # /proc/self/fd/x is a pseudo-symlink to the file open on
            # fd x.
            if (
                os.path.exists(path) is True
                # and os.path.islink(path) is True
                and "/fd/" in path
            ):
                return True
        except Exception:
            return False
    else:  # pragma: no cover
        return False


def read_file(path: str) -> Optional[str]:
    """Read file contents.

    Args:
        path (str): Path to file.

    Raises:
        OSError: If path does not exist.
        OSError: If path is a directory.
        OSError: If path is not a file.

    Returns:
        Optional[str]: File contents.
    """
    if os.path.exists(path) is False:
        raise OSError("Path does not exist. %s" % path)

    # Resolve symlinks
    if os.path.islink(path) is True:
        # Avoid trying to resolve file descriptors
        # as symlinks.
        if "/fd/" in path:  # pragma: no cover
            fd_sp = path.split("/")
            fd_num = int(fd_sp[-1])
            with os.fdopen(fd_num, mode="r", encoding="utf-8") as fd:
                return fd.read()

        # Resolve symlinks to non-descriptors
        path = os.readlink(path)  # pragma: no cover

    # Read simple file
    if os.path.isfile(path) is True:
        with open(path, encoding="utf-8") as f:
            return f.read()

    # Raise error if path is a directory
    elif os.path.isdir(path) is True:
        raise OSError("Path is a directory. %s" % path)

    # Raise error if path is not a file
    else:
        raise OSError("Path is not a file. %s" % path)
