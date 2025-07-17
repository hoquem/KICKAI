"""
Cache Strategies

This module provides different caching strategies for the application.
"""

import json
import logging
import time
import os
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheStrategy(ABC):
    """Abstract base class for cache strategies."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache entries."""
        pass


class InMemoryCacheStrategy(CacheStrategy):
    """In-memory cache strategy."""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.access_times: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if entry has expired
        if 'expires_at' in entry and entry['expires_at'] < time.time():
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            return None
        
        # Update access time
        self.access_times[key] = time.time()
        
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache."""
        # Check if cache is full and evict if necessary
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._evict_oldest()
        
        entry = {
            'value': value,
            'created_at': time.time()
        }
        
        if ttl:
            entry['expires_at'] = time.time() + ttl
        
        self.cache[key] = entry
        self.access_times[key] = time.time()
        
        return True
    
    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        if key in self.cache:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            return True
        return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        self.cache.clear()
        self.access_times.clear()
        return True
    
    def _evict_oldest(self) -> None:
        """Evict the oldest accessed entry."""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.cache[oldest_key]
        del self.access_times[oldest_key]


class RedisCacheStrategy(CacheStrategy):
    """Redis cache strategy."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis_client = None
        self._connect()
    
    def _connect(self) -> None:
        """Connect to Redis."""
        try:
            import redis
            self._redis_client = redis.from_url(self.redis_url)
            # Test connection
            self._redis_client.ping()
            logger.info("Connected to Redis cache")
        except ImportError:
            logger.warning("Redis not available, falling back to in-memory cache")
            self._redis_client = None
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis cache."""
        if not self._redis_client:
            return None
        
        try:
            value = self._redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting from Redis cache: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in Redis cache."""
        if not self._redis_client:
            return False
        
        try:
            serialized_value = json.dumps(value)
            if ttl:
                return self._redis_client.setex(key, ttl, serialized_value)
            else:
                return self._redis_client.set(key, serialized_value)
        except Exception as e:
            logger.error(f"Error setting in Redis cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a value from Redis cache."""
        if not self._redis_client:
            return False
        
        try:
            return bool(self._redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting from Redis cache: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        if not self._redis_client:
            return False
        
        try:
            self._redis_client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Error clearing Redis cache: {e}")
            return False


class FileCacheStrategy(CacheStrategy):
    """File-based cache strategy."""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self) -> None:
        """Ensure cache directory exists."""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating cache directory: {e}")
    
    def _get_cache_file_path(self, key: str) -> str:
        """Get cache file path for a key."""
        import hashlib
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{safe_key}.json")
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from file cache."""
        try:
            file_path = self._get_cache_file_path(key)
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r') as f:
                entry = json.load(f)
            
            # Check if entry has expired
            if 'expires_at' in entry and entry['expires_at'] < time.time():
                os.remove(file_path)
                return None
            
            return entry['value']
        except Exception as e:
            logger.error(f"Error getting from file cache: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in file cache."""
        try:
            entry = {
                'value': value,
                'created_at': time.time()
            }
            
            if ttl:
                entry['expires_at'] = time.time() + ttl
            
            file_path = self._get_cache_file_path(key)
            with open(file_path, 'w') as f:
                json.dump(entry, f)
            
            return True
        except Exception as e:
            logger.error(f"Error setting in file cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a value from file cache."""
        try:
            file_path = self._get_cache_file_path(key)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting from file cache: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)
            return True
        except Exception as e:
            logger.error(f"Error clearing file cache: {e}")
            return False 