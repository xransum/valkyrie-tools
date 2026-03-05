"""Cache module for in-memory function-result caching.

Provides two caching strategies via the :class:`Cache` decorator class:

* **Memoize** (:meth:`Cache.memoize`) - a simple dict-backed cache that stores
  every unique argument tuple indefinitely (no size limit, no expiry).
* **TTL cache** (:meth:`Cache.ttl_cache`) - wraps :func:`functools.lru_cache`
  with a time-based hash so that results expire automatically after a
  configurable number of seconds.

A package-level singleton (:data:`cache`) is available for convenience so that
individual modules do not need to instantiate :class:`Cache` themselves.
"""

from functools import lru_cache, update_wrapper
from math import floor
from time import time
from typing import Any, Callable


def _ttl_hash_gen(seconds: int) -> int:
    """Generates a hash value based on the elapsed time.

    Since the start of the generator, divided by the specified number of seconds.

    Args:
        seconds (int): The number of seconds to divide the elapsed time by.

    Yields:
        int: The hash value generated based on the elapsed time.
    """
    start_time = time()
    while True:
        yield floor((time() - start_time) / seconds)


class Cache:
    """A decorator class for caching function results."""

    @staticmethod
    def memoize(fn: Callable) -> Callable:
        """Decorator for caching function results.

        Memoize decorator that caches the return value of a function
        based on its arguments.

        Args:
            fn (Callable): The function to be memoized.

        Returns:
            Callable: The memoized function.

        Example:
            >>> from valkyrie_tools.cache import Cache
            >>> cache = Cache()
            >>> call_count = [0]
            >>> @cache.memoize
            ... def expensive(x):
            ...     call_count[0] += 1
            ...     return x * 2
            >>> expensive(3)
            6
            >>> expensive(3)  # returns cached result
            6
            >>> call_count[0]  # only called once
            1
        """
        memo = {}

        def wrapper(*args: Any) -> Any:
            """A wrapper that caches the result of the function."""
            if args in memo:
                return memo[args]
            else:
                rv = fn(*args)
                memo[args] = rv
                return rv

        return wrapper

    @staticmethod
    def ttl_cache(
        maxsize: int = 128, typed: bool = False, ttl: int = -1
    ) -> Callable:
        """Decorator that adds TTL caching functionality to a function.

        Wraps :func:`functools.lru_cache` with a time-based hash so that
        cached results expire after ``ttl`` seconds.

        Args:
            maxsize (int): The maximum number of function calls to
                cache. Defaults to 128.
            typed (bool): Whether to differentiate between
                arguments of different types. Defaults to False.
            ttl (int): The time-to-live (in seconds) for the cached
                function results. Defaults to -1, which means no expiration
                (effectively ``65536`` seconds).

        Returns:
            Callable: The decorated function.  The returned wrapper also
            exposes a ``clear_cache()`` method to manually invalidate the
            underlying ``lru_cache``.

        Example:
            >>> from valkyrie_tools.cache import Cache
            >>> cache = Cache()
            >>> @cache.ttl_cache(maxsize=64, ttl=300)
            ... def fetch_data(key):
            ...     return f"data:{key}"
            >>> fetch_data("x")
            'data:x'
            >>> fetch_data("x")  # served from cache within TTL window
            'data:x'
            >>> fetch_data.clear_cache()  # invalidate manually if needed
        """
        # Any ttl that's 0 or less, set to max.
        if ttl <= 0:
            ttl = 65536  # pragma: no cover

        hash_gen = _ttl_hash_gen(ttl)

        def wrapper(func: Callable) -> Callable:
            """A decorator that adds caching functionality to a function.

            Args:
                func (Callable): The function to be decorated.

            Returns:
                Callable: The decorated function.
            """

            @lru_cache(maxsize, typed)
            def ttl_func(ttl_hash: str, *args, **kwargs) -> Any:
                """Caches the result of 'func' function based on the arguments.

                Args:
                    ttl_hash (str): Hash used to identify the cached result.
                    *args: Positional arguments passed to the 'func' function.
                    **kwargs: Keyword arguments passed to the 'func' function.

                Returns:
                    The result of the 'func' function.
                """
                return func(*args, **kwargs)

            def wrapped(*args, **kwargs) -> Any:
                """A wrapper that generates a hash value and calls the ttl_func.

                This function is a wrapper that generates a hash value and
                calls the ttl_func with the generated hash value, along with
                the provided arguments and keyword arguments.

                Args:
                    *args: Variable length argument list.
                    **kwargs: Arbitrary keyword arguments.

                Returns:
                    Any: The result returned by ttl_func.
                """
                th = next(hash_gen)
                return ttl_func(th, *args, **kwargs)

            def clear_cache() -> Any:
                """Clears the cache used by the ttl_func."""
                ttl_func.cache_clear()

            wrapped.clear_cache = clear_cache

            return update_wrapper(wrapped, func)

        return wrapper


cache = Cache()
"""Package-level :class:`Cache` singleton.

Used throughout the package as ``@cache.memoize`` and
``@cache.ttl_cache(...)`` decorators so that individual modules do not need to
instantiate :class:`Cache` themselves.
"""
