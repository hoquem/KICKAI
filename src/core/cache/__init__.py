"""
Core caching system for KICKAI.

This package provides a clean, layered caching architecture that follows
clean architecture principles and OOP best practices.
"""

from .cache_manager import CacheManager, get_cache_manager, initialize_cache_manager
from .cache_strategies import (
    CacheStrategy,
    NoCacheStrategy,
    MemoryCacheStrategy,
    TTLMemoryCacheStrategy
)
from .cache_keys import CacheKey, CacheKeyBuilder
from .cache_interfaces import ICacheProvider, ICacheStrategy

__all__ = [
    'CacheManager',
    'get_cache_manager',
    'initialize_cache_manager',
    'CacheStrategy',
    'NoCacheStrategy', 
    'MemoryCacheStrategy',
    'TTLMemoryCacheStrategy',
    'CacheKey',
    'CacheKeyBuilder',
    'ICacheProvider',
    'ICacheStrategy'
] 