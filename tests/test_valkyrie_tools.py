"""Test cases for the valkyrie_tools module."""

import sys
from importlib.metadata import PackageNotFoundError
from unittest.mock import patch

from valkyrie_tools import __version__


def test_version() -> None:
    """Test the version."""
    assert 3 == len(__version__.split("."))


def test_version_is_not_unknown() -> None:
    """Test that importlib.metadata resolved the version from package metadata."""
    assert __version__ != "unknown"


def test_version_fallback_when_package_not_found() -> None:
    """Test that __version__ falls back to 'unknown' if the package is not installed."""
    import valkyrie_tools

    with patch(
        "importlib.metadata.version",
        side_effect=PackageNotFoundError("valkyrie_tools"),
    ):
        # Force reimport so the try/except block re-executes.
        if "valkyrie_tools" in sys.modules:
            del sys.modules["valkyrie_tools"]
        import valkyrie_tools as vt_reloaded

        assert vt_reloaded.__version__ == "unknown"

    # Restore the original module so other tests are unaffected.
    sys.modules["valkyrie_tools"] = valkyrie_tools
