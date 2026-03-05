"""Cache module tests."""

import unittest
from time import sleep
from typing import Any

from valkyrie_tools.cache import _ttl_hash_gen, cache


class TestTTLHashGen(unittest.TestCase):
    """Test case for the _ttl_hash_gen function."""

    def test_ttl_hash_gen(self) -> None:
        """Test _ttl_hash_gen function."""
        gen = _ttl_hash_gen(1)
        first = next(gen)
        sleep(1)
        second = next(gen)
        self.assertGreater(second, first)


class TestCache(unittest.TestCase):
    """Test case for the cache class."""

    def test_memoize(self) -> None:
        """Test memoize function."""

        @cache.memoize
        def add(a: Any, b: Any) -> Any:
            return a + b

        self.assertEqual(add(1, 2), 3)
        # should return cached result
        self.assertEqual(add(1, 2), 3)

    def test_ttl_cache(self) -> None:
        """Test ttl_cache function."""

        @cache.ttl_cache(ttl=1)
        def add(a: Any, b: Any) -> Any:
            return a + b

        self.assertEqual(add(1, 2), 3)
        sleep(1)
        # should compute result again after ttl
        self.assertEqual(add(1, 2), 3)

    def test_clear_cache(self) -> None:
        """Test clear_cache function."""

        @cache.ttl_cache(ttl=1)
        def add(a: Any, b: Any) -> Any:
            return a + b

        self.assertEqual(add(1, 2), 3)
        add.clear_cache()  # type: ignore[attr-defined]  # noqa: B950
        # should compute result again after cache clear
        self.assertEqual(add(1, 2), 3)
