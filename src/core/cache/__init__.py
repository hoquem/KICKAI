"""
Core caching system for KICKAI.

This package provides a clean, layered caching architecture that follows
clean architecture principles and OOP best practices.
"""

from core.cache.cache_manager import CacheManager, get_cache_manager, initialize_cache_manager
from core.cache.cache_strategies import (
    MemoryCacheStrategy,
    RedisCacheStrategy,
    FileCacheStrategy,
    CompositeCacheStrategy
)
from core.cache.cache_keys import CacheKey, CacheKeyBuilder
from core.cache.cache_interfaces import ICacheProvider, ICacheStrategy

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