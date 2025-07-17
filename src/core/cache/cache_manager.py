"""
Cache manager for the KICKAI caching system.

This module provides the main cache manager that orchestrates different
cache strategies and provides a clean, unified API for caching operations.
"""

import logging
from typing import Any, Optional, Dict, List
from datetime import datetime

from core.cache.cache_interfaces import ICacheProvider, ICacheStrategy
from core.cache.cache_strategies import (
    MemoryCacheStrategy,
    RedisCacheStrategy,
    FileCacheStrategy,
    CompositeCacheStrategy
)
from core.cache.cache_keys import CacheKey, CacheKeyBuilder

logger = logging.getLogger(__name__)


class CacheManager(ICacheProvider):
    """
    Main cache manager that orchestrates different cache strategies.
    
    This class provides a clean, unified API for caching operations
    while supporting multiple cache strategies for different types of data.
    """
    
    def __init__(self):
        """Initialize the cache manager with default strategies."""
        self._strategies: Dict[str, ICacheStrategy] = {}
        self._default_strategy = "default"
        
        # Initialize default strategies
        self._initialize_default_strategies()
        
        logger.info("CacheManager initialized with default strategies")
    
    def _initialize_default_strategies(self):
        """Initialize default cache strategies."""
        # Default strategy - TTL memory cache with 1 hour default TTL
        self._strategies["default"] = TTLMemoryCacheStrategy(
            max_size=1000,
            default_ttl=3600  # 1 hour
        )
        
        # Long-term cache for static data (team mappings, configs)
        self._strategies["static"] = TTLMemoryCacheStrategy(
            max_size=500,
            default_ttl=86400  # 24 hours
        )
        
        # Short-term cache for session data
        self._strategies["session"] = TTLMemoryCacheStrategy(
            max_size=200,
            default_ttl=1800  # 30 minutes
        )
        
        # No-cache strategy for testing/debugging
        self._strategies["no_cache"] = NoCacheStrategy()
        
        logger.info(f"Initialized {len(self._strategies)} cache strategies")
    
    def register_strategy(self, name: str, strategy: ICacheStrategy) -> None:
        """Register a new cache strategy."""
        self._strategies[name] = strategy
        logger.info(f"Registered cache strategy: {name}")
    
    def get_strategy(self, strategy_name: str) -> ICacheStrategy:
        """Get a cache strategy by name."""
        if strategy_name not in self._strategies:
            logger.warning(f"Cache strategy '{strategy_name}' not found, using default")
            return self._strategies[self._default_strategy]
        return self._strategies[strategy_name]
    
    def get(self, key: str, strategy: str = "default") -> Optional[Any]:
        """Get a value using the specified strategy."""
        cache_strategy = self.get_strategy(strategy)
        result = cache_strategy.get(key)
        
        if result is not None:
            logger.debug(f"Cache HIT: {key} (strategy: {strategy})")
        else:
            logger.debug(f"Cache MISS: {key} (strategy: {strategy})")
        
        return result
    
    def set(self, key: str, value: Any, strategy: str = "default", ttl: Optional[int] = None) -> bool:
        """Set a value using the specified strategy."""
        cache_strategy = self.get_strategy(strategy)
        success = cache_strategy.set(key, value, ttl)
        
        if success:
            logger.debug(f"Cache SET: {key} (strategy: {strategy}, ttl: {ttl})")
        else:
            logger.warning(f"Cache SET FAILED: {key} (strategy: {strategy})")
        
        return success
    
    def delete(self, key: str, strategy: str = "default") -> bool:
        """Delete a value using the specified strategy."""
        cache_strategy = self.get_strategy(strategy)
        success = cache_strategy.delete(key)
        
        if success:
            logger.debug(f"Cache DELETE: {key} (strategy: {strategy})")
        
        return success
    
    def clear(self, strategy: str = "default") -> bool:
        """Clear cache using the specified strategy."""
        cache_strategy = self.get_strategy(strategy)
        success = cache_strategy.clear()
        
        if success:
            logger.info(f"Cache CLEAR: {strategy}")
        
        return success
    
    def exists(self, key: str, strategy: str = "default") -> bool:
        """Check if a key exists using the specified strategy."""
        cache_strategy = self.get_strategy(strategy)
        return cache_strategy.exists(key)
    
    def get_stats(self, strategy: str = "default") -> Dict[str, Any]:
        """Get cache statistics for the specified strategy."""
        cache_strategy = self.get_strategy(strategy)
        return cache_strategy.get_stats()
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all cache strategies."""
        return {
            name: strategy.get_stats()
            for name, strategy in self._strategies.items()
        }
    
    # Convenience methods for common operations
    
    def get_team_mapping(self, chat_id: str) -> Optional[str]:
        """Get team ID for a chat ID from cache."""
        cache_key = str(CacheKeyBuilder.team_mapping(chat_id))
        return self.get(cache_key, "static")
    
    def set_team_mapping(self, chat_id: str, team_id: str) -> bool:
        """Set team ID mapping for a chat ID in cache."""
        cache_key = str(CacheKeyBuilder.team_mapping(chat_id))
        return self.set(cache_key, team_id, "static", ttl=86400)  # 24 hours
    
    def get_team_config(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Get team configuration from cache."""
        cache_key = str(CacheKeyBuilder.team_config(team_id))
        return self.get(cache_key, "static")
    
    def set_team_config(self, team_id: str, config: Dict[str, Any]) -> bool:
        """Set team configuration in cache."""
        cache_key = str(CacheKeyBuilder.team_config(team_id))
        return self.set(cache_key, config, "static", ttl=86400)  # 24 hours
    
    def get_player_data(self, team_id: str, player_id: str) -> Optional[Dict[str, Any]]:
        """Get player data from cache."""
        cache_key = str(CacheKeyBuilder.player_data(team_id, player_id))
        return self.get(cache_key, "default")
    
    def set_player_data(self, team_id: str, player_id: str, data: Dict[str, Any]) -> bool:
        """Set player data in cache."""
        cache_key = str(CacheKeyBuilder.player_data(team_id, player_id))
        return self.set(cache_key, data, "default", ttl=3600)  # 1 hour
    
    def get_player_by_telegram_id(self, team_id: str, telegram_id: str) -> Optional[Dict[str, Any]]:
        """Get player data by Telegram ID from cache."""
        cache_key = str(CacheKeyBuilder.player_by_telegram_id(team_id, telegram_id))
        return self.get(cache_key, "default")
    
    def set_player_by_telegram_id(self, team_id: str, telegram_id: str, data: Dict[str, Any]) -> bool:
        """Set player data by Telegram ID in cache."""
        cache_key = str(CacheKeyBuilder.player_by_telegram_id(team_id, telegram_id))
        return self.set(cache_key, data, "default", ttl=3600)  # 1 hour
    
    def invalidate_player_data(self, team_id: str, player_id: str) -> bool:
        """Invalidate player data cache."""
        cache_key = str(CacheKeyBuilder.player_data(team_id, player_id))
        return self.delete(cache_key, "default")
    
    def invalidate_team_data(self, team_id: str) -> bool:
        """Invalidate all team-related cache entries."""
        # This is a simple implementation - in a more sophisticated system,
        # we might want to use cache tags or patterns
        logger.info(f"Invalidating team data for team: {team_id}")
        return True  # Placeholder - would need pattern-based deletion
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get comprehensive cache information."""
        all_stats = self.get_all_stats()
        
        total_hits = sum(stats.get("hits", 0) for stats in all_stats.values())
        total_misses = sum(stats.get("misses", 0) for stats in all_stats.values())
        total_requests = total_hits + total_misses
        overall_hit_rate = total_hits / total_requests if total_requests > 0 else 0.0
        
        return {
            "strategies": list(self._strategies.keys()),
            "default_strategy": self._default_strategy,
            "overall_hit_rate": overall_hit_rate,
            "total_requests": total_requests,
            "strategy_stats": all_stats
        }


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance (singleton pattern)."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def initialize_cache_manager() -> CacheManager:
    """Initialize the global cache manager."""
    global _cache_manager
    if _cache_manager is not None:
        logger.warning("Cache manager already initialized")
        return _cache_manager
    
    _cache_manager = CacheManager()
    logger.info("Global cache manager initialized")
    return _cache_manager 