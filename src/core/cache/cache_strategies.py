"""
Cache strategies for the KICKAI caching system.

This module provides different caching strategies with varying TTL
and storage mechanisms for different types of data.
"""

import time
import logging
from typing import Any, Optional, Dict, Tuple
from datetime import datetime, timedelta
from .cache_interfaces import ICacheStrategy

logger = logging.getLogger(__name__)


class CacheStrategy(ICacheStrategy):
    """Base cache strategy class."""
    
    def __init__(self, name: str):
        self.name = name
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "created_at": datetime.now()
        }
    
    def _log_hit(self):
        """Log a cache hit."""
        self.stats["hits"] += 1
    
    def _log_miss(self):
        """Log a cache miss."""
        self.stats["misses"] += 1
    
    def _log_set(self):
        """Log a cache set operation."""
        self.stats["sets"] += 1
    
    def _log_delete(self):
        """Log a cache delete operation."""
        self.stats["deletes"] += 1
    
    def get_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.stats["hits"] + self.stats["misses"]
        return self.stats["hits"] / total if total > 0 else 0.0


class NoCacheStrategy(CacheStrategy):
    """Strategy that doesn't cache anything (for testing/debugging)."""
    
    def __init__(self):
        super().__init__("no_cache")
    
    def get(self, key: str) -> Optional[Any]:
        """Always return None (no caching)."""
        self._log_miss()
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Do nothing (no caching)."""
        self._log_set()
        return True
    
    def delete(self, key: str) -> bool:
        """Do nothing (no caching)."""
        self._log_delete()
        return True
    
    def clear(self) -> bool:
        """Do nothing (no caching)."""
        return True
    
    def exists(self, key: str) -> bool:
        """Always return False (no caching)."""
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            **self.stats,
            "hit_rate": self.get_hit_rate(),
            "strategy": "no_cache"
        }


class MemoryCacheStrategy(CacheStrategy):
    """Simple in-memory cache strategy."""
    
    def __init__(self, max_size: int = 1000):
        super().__init__("memory")
        self.max_size = max_size
        self._cache: Dict[str, Any] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if key in self._cache:
            self._log_hit()
            return self._cache[key]
        else:
            self._log_miss()
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache."""
        # Simple LRU eviction if cache is full
        if len(self._cache) >= self.max_size and key not in self._cache:
            # Remove oldest item (simple implementation)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        self._cache[key] = value
        self._log_set()
        return True
    
    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        if key in self._cache:
            del self._cache[key]
            self._log_delete()
            return True
        return False
    
    def clear(self) -> bool:
        """Clear all cached values."""
        self._cache.clear()
        return True
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        return key in self._cache
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            **self.stats,
            "hit_rate": self.get_hit_rate(),
            "strategy": "memory",
            "size": len(self._cache),
            "max_size": self.max_size
        }


class TTLMemoryCacheStrategy(CacheStrategy):
    """Time-to-live in-memory cache strategy."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        super().__init__("ttl_memory")
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, Tuple[Any, float]] = {}  # (value, expiry_time)
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache, checking TTL."""
        if key in self._cache:
            value, expiry_time = self._cache[key]
            if time.time() < expiry_time:
                self._log_hit()
                return value
            else:
                # Expired, remove it
                del self._cache[key]
        
        self._log_miss()
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache with TTL."""
        # Use provided TTL or default
        ttl_seconds = ttl if ttl is not None else self.default_ttl
        expiry_time = time.time() + ttl_seconds
        
        # Simple LRU eviction if cache is full
        if len(self._cache) >= self.max_size and key not in self._cache:
            # Remove oldest item (simple implementation)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        self._cache[key] = (value, expiry_time)
        self._log_set()
        return True
    
    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        if key in self._cache:
            del self._cache[key]
            self._log_delete()
            return True
        return False
    
    def clear(self) -> bool:
        """Clear all cached values."""
        self._cache.clear()
        return True
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in cache and is not expired."""
        if key in self._cache:
            _, expiry_time = self._cache[key]
            if time.time() < expiry_time:
                return True
            else:
                # Expired, remove it
                del self._cache[key]
        return False
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed items."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry_time) in self._cache.items()
            if current_time >= expiry_time
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        # Clean up expired entries before reporting stats
        expired_count = self.cleanup_expired()
        
        return {
            **self.stats,
            "hit_rate": self.get_hit_rate(),
            "strategy": "ttl_memory",
            "size": len(self._cache),
            "max_size": self.max_size,
            "default_ttl": self.default_ttl,
            "expired_cleaned": expired_count
        } 