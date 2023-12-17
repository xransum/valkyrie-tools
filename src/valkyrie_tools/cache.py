"""Cache module for persistent data."""
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
    """A decorator class for caching function results.

    Usage:
    @cache.memoize
    def my_function(arg1, arg2):
        # function body

    @cache.ttl_cache(maxsize=128, typed=False, ttl=-1)
    def my_function(arg1, arg2):
        # function body
    """

    @staticmethod
    def memoize(fn: Callable) -> Callable:
        """Decorator for caching function results.

        Memoize decorator that caches the return value of a function
        based on its arguments.

        Args:
            fn (Callable): The function to be memoized.

        Returns:
            The memoized function.
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

        Args:
            maxsize (int): The maximum number of function calls to
                cache. Defaults to 128.
            typed (bool): Whether to differentiate between
                arguments of different types. Defaults to False.
            ttl (int): The time-to-live (in seconds) for the cached
                function results. Defaults to -1, which means no expiration.

        Returns:
            Callable: The decorated function.
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
