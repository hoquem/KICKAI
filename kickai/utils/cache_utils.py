#!/usr/bin/env python3
"""
Cache Utilities

This module provides simple caching utilities for frequently accessed data.
"""

import asyncio
import time
from typing import Any, Dict, Optional, TypeVar, Generic
from dataclasses import dataclass
from loguru import logger

T = TypeVar('T')


@dataclass
class CacheEntry(Generic[T]):
    """A cache entry with value and expiration time."""
    value: T
    created_at: float
    expires_at: float
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return time.time() > self.expires_at


class SimpleCache:
    """A simple in-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self._cache: Dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            
            if entry.is_expired():
                del self._cache[key]
                return None
            
            return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)
        """
        async with self._lock:
            ttl = ttl or self._default_ttl
            expires_at = time.time() + ttl
            
            self._cache[key] = CacheEntry(
                value=value,
                created_at=time.time(),
                expires_at=expires_at
            )
    
    async def delete(self, key: str) -> None:
        """
        Delete a key from cache.
        
        Args:
            key: Cache key to delete
        """
        async with self._lock:
            self._cache.pop(key, None)
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
    
    async def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            return len(expired_keys)
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        async with self._lock:
            total_entries = len(self._cache)
            expired_entries = sum(1 for entry in self._cache.values() if entry.is_expired())
            active_entries = total_entries - expired_entries
            
            return {
                "total_entries": total_entries,
                "active_entries": active_entries,
                "expired_entries": expired_entries,
                "cache_size": len(self._cache)
            }


# Global cache instance
_cache = SimpleCache()


def get_cache() -> SimpleCache:
    """Get the global cache instance."""
    return _cache


class CacheManager:
    """Manager for different types of cached data."""
    
    def __init__(self):
        self._cache = get_cache()
    
    async def get_team_config(self, team_id: str) -> Optional[Dict[str, Any]]:
        """
        Get team configuration from cache.
        
        Args:
            team_id: Team ID
            
        Returns:
            Team configuration or None if not cached
        """
        return await self._cache.get(f"team_config:{team_id}")
    
    async def set_team_config(self, team_id: str, config: Dict[str, Any], ttl: int = 600) -> None:
        """
        Cache team configuration.
        
        Args:
            team_id: Team ID
            config: Team configuration
            ttl: Time to live in seconds (10 minutes default)
        """
        await self._cache.set(f"team_config:{team_id}", config, ttl)
    
    async def get_player_list(self, team_id: str) -> Optional[list]:
        """
        Get player list from cache.
        
        Args:
            team_id: Team ID
            
        Returns:
            Player list or None if not cached
        """
        return await self._cache.get(f"player_list:{team_id}")
    
    async def set_player_list(self, team_id: str, players: list, ttl: int = 300) -> None:
        """
        Cache player list.
        
        Args:
            team_id: Team ID
            players: Player list
            ttl: Time to live in seconds (5 minutes default)
        """
        await self._cache.set(f"player_list:{team_id}", players, ttl)
    
    async def invalidate_team_data(self, team_id: str) -> None:
        """
        Invalidate all cached data for a team.
        
        Args:
            team_id: Team ID
        """
        await self._cache.delete(f"team_config:{team_id}")
        await self._cache.delete(f"player_list:{team_id}")
        logger.info(f"Invalidated cache for team: {team_id}")
    
    async def get_invite_link(self, invite_id: str) -> Optional[Dict[str, Any]]:
        """
        Get invite link from cache.
        
        Args:
            invite_id: Invite link ID
            
        Returns:
            Invite link data or None if not cached
        """
        return await self._cache.get(f"invite_link:{invite_id}")
    
    async def set_invite_link(self, invite_id: str, link_data: Dict[str, Any], ttl: int = 3600) -> None:
        """
        Cache invite link data.
        
        Args:
            invite_id: Invite link ID
            link_data: Invite link data
            ttl: Time to live in seconds (1 hour default)
        """
        await self._cache.set(f"invite_link:{invite_id}", link_data, ttl)


# Global cache manager instance
_cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    return _cache_manager


async def periodic_cache_cleanup():
    """Periodic task to clean up expired cache entries."""
    cache = get_cache()
    while True:
        try:
            await asyncio.sleep(60)  # Run every minute
            await cache.cleanup_expired()
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")


def start_cache_cleanup_task():
    """Start the periodic cache cleanup task."""
    loop = asyncio.get_event_loop()
    loop.create_task(periodic_cache_cleanup())
    logger.info("Started periodic cache cleanup task") 