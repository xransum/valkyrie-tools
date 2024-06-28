"""Test cases for the valkyrie_tools module."""

from valkyrie_tools import __version__


def test_version() -> None:
    """Test the version."""
    assert 3 == len(__version__.split("."))
