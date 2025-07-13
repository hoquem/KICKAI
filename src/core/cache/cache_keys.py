"""
Cache key management for the KICKAI caching system.

This module provides a clean way to generate and manage cache keys
with proper namespacing and versioning.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class CacheNamespace(Enum):
    """Cache namespaces for different types of data."""
    TEAM_MAPPING = "team_mapping"
    TEAM_CONFIG = "team_config"
    PLAYER_DATA = "player_data"
    MATCH_DATA = "match_data"
    SYSTEM_CONFIG = "system_config"
    USER_SESSION = "user_session"


@dataclass
class CacheKey:
    """Represents a cache key with namespace and components."""
    namespace: CacheNamespace
    components: Dict[str, str]
    version: str = "v1"
    
    def __str__(self) -> str:
        """Generate the cache key string."""
        component_str = ":".join(f"{k}={v}" for k, v in sorted(self.components.items()))
        return f"{self.namespace.value}:{self.version}:{component_str}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "namespace": self.namespace.value,
            "components": self.components,
            "version": self.version
        }


class CacheKeyBuilder:
    """Builder for creating cache keys with proper structure."""
    
    @staticmethod
    def team_mapping(chat_id: str) -> CacheKey:
        """Create a cache key for team mapping by chat ID."""
        return CacheKey(
            namespace=CacheNamespace.TEAM_MAPPING,
            components={"chat_id": str(chat_id)}
        )
    
    @staticmethod
    def team_config(team_id: str) -> CacheKey:
        """Create a cache key for team configuration."""
        return CacheKey(
            namespace=CacheNamespace.TEAM_CONFIG,
            components={"team_id": team_id}
        )
    
    @staticmethod
    def player_data(team_id: str, player_id: str) -> CacheKey:
        """Create a cache key for player data."""
        return CacheKey(
            namespace=CacheNamespace.PLAYER_DATA,
            components={"team_id": team_id, "player_id": player_id}
        )
    
    @staticmethod
    def player_by_telegram_id(team_id: str, telegram_id: str) -> CacheKey:
        """Create a cache key for player lookup by Telegram ID."""
        return CacheKey(
            namespace=CacheNamespace.PLAYER_DATA,
            components={"team_id": team_id, "telegram_id": telegram_id}
        )
    
    @staticmethod
    def match_data(team_id: str, match_id: str) -> CacheKey:
        """Create a cache key for match data."""
        return CacheKey(
            namespace=CacheNamespace.MATCH_DATA,
            components={"team_id": team_id, "match_id": match_id}
        )
    
    @staticmethod
    def system_config(config_key: str) -> CacheKey:
        """Create a cache key for system configuration."""
        return CacheKey(
            namespace=CacheNamespace.SYSTEM_CONFIG,
            components={"config_key": config_key}
        )
    
    @staticmethod
    def user_session(user_id: str, session_type: str = "default") -> CacheKey:
        """Create a cache key for user session data."""
        return CacheKey(
            namespace=CacheNamespace.USER_SESSION,
            components={"user_id": str(user_id), "session_type": session_type}
        ) 