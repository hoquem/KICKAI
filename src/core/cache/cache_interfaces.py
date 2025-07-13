"""
Cache interfaces for the KICKAI caching system.

This module defines the core interfaces that follow clean architecture
principles and provide a clean abstraction for caching operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List
from datetime import datetime


class ICacheStrategy(ABC):
    """Interface for cache strategies."""
    
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
        """Clear all cached values."""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass


class ICacheProvider(ABC):
    """Interface for cache providers."""
    
    @abstractmethod
    def get(self, key: str, strategy: str = "default") -> Optional[Any]:
        """Get a value using the specified strategy."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, strategy: str = "default", ttl: Optional[int] = None) -> bool:
        """Set a value using the specified strategy."""
        pass
    
    @abstractmethod
    def delete(self, key: str, strategy: str = "default") -> bool:
        """Delete a value using the specified strategy."""
        pass
    
    @abstractmethod
    def clear(self, strategy: str = "default") -> bool:
        """Clear cache using the specified strategy."""
        pass
    
    @abstractmethod
    def exists(self, key: str, strategy: str = "default") -> bool:
        """Check if a key exists using the specified strategy."""
        pass
    
    @abstractmethod
    def get_stats(self, strategy: str = "default") -> Dict[str, Any]:
        """Get cache statistics for the specified strategy."""
        pass
    
    @abstractmethod
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all cache strategies."""
        pass 