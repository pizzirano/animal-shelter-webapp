"""
Cache management utilities.
"""
from django.core.cache import cache # pyright: ignore[reportMissingModuleSource]
from django.conf import settings # pyright: ignore[reportMissingModuleSource]
from functools import wraps

def cache_function(timeout=300, key_prefix=''):
    """
    Decorator that caches the result of a function.

    Usage:
        @cache_function(timeout=600, key_prefix='my_func')
        def my_expensive_function(arg1, arg2):
            return expensive_computation()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build the cache key from the arguments
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to read from the cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Compute and store in the cache
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result

        return wrapper
    return decorator


def invalidate_cache_by_prefix(prefix):
    """
    Invalidate every cache key matching a given prefix (Redis only).
    """
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern(f"*{prefix}*")
    else:
        # Fallback for other backends
        cache.clear()


def get_or_set_cache(key, default_func, timeout=300):
    """
    Get a cached value or set it from a default callable.

    Usage:
        dogs = get_or_set_cache(
            'all_dogs',
            lambda: Dog.objects.all(),
            timeout=600
        )
    """
    value = cache.get(key)
    if value is None:
        value = default_func()
        cache.set(key, value, timeout)
    return value
