#!/usr/bin/env python3
"""
Memory Manager for KICKAI System - CrewAI 0.157.0 Enhanced Memory

This module provides entity-specific memory management for the KICKAI system,
enabling better context retention and agent coordination.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta

from crewai import memory
from loguru import logger

from kickai.core.enums import AgentRole, EntityType
from kickai.core.config import get_settings


@dataclass
class MemoryEntry:
    """A single memory entry with metadata."""
    
    key: str
    value: Any
    entity_type: EntityType
    entity_id: str
    timestamp: datetime
    ttl: Optional[timedelta] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def is_expired(self) -> bool:
        """Check if the memory entry has expired."""
        if self.ttl is None:
            return False
        return datetime.now() > self.timestamp + self.ttl


class KICKAIMemoryManager:
    """
    Memory manager for KICKAI system with entity-specific memory support.
    
    Features:
    - Entity-specific memory (players, team members, teams)
    - Short-term and long-term memory
    - Automatic cleanup and TTL support
    - Integration with CrewAI memory systems
    """
    
    def __init__(self):
        """Initialize the memory manager."""
        self.settings = get_settings()
        
        # Initialize CrewAI memory systems
        self._initialize_crewai_memory()
        
        # Local memory cache for fast access
        self._local_cache: Dict[str, MemoryEntry] = {}
        
        logger.info("🧠 KICKAI Memory Manager initialized")
    
    def _initialize_crewai_memory(self):
        """Initialize CrewAI memory systems with graceful fallback."""
        try:
            # Try to initialize LongTermMemory first (most stable)
            self.long_term_memory = memory.LongTermMemory()
            logger.info("✅ CrewAI LongTermMemory initialized")
            
            # EntityMemory and ShortTermMemory require ChromaDB which may be corrupted
            # Initialize with fallback to local memory
            try:
                self.player_memory = memory.EntityMemory()
                self.team_member_memory = memory.EntityMemory() 
                self.team_memory = memory.EntityMemory()
                logger.info("✅ CrewAI EntityMemory systems initialized")
            except Exception as entity_error:
                logger.warning(f"⚠️ CrewAI EntityMemory failed (ChromaDB issue): {entity_error}")
                logger.info("🔄 Using local memory proxy for entity memory")
                self.player_memory = None
                self.team_member_memory = None
                self.team_memory = None
            
            try:
                self.short_term_memory = memory.ShortTermMemory()
                logger.info("✅ CrewAI ShortTermMemory initialized")
            except Exception as short_term_error:
                logger.warning(f"⚠️ CrewAI ShortTermMemory failed (ChromaDB issue): {short_term_error}")
                logger.info("🔄 Using local memory proxy for short-term memory")
                self.short_term_memory = None
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize any CrewAI memory systems: {e}")
            # Complete fallback to local memory only
            self.player_memory = None
            self.team_member_memory = None
            self.team_memory = None
            self.short_term_memory = None
            self.long_term_memory = None
    
    def get_memory_for_agent(self, agent_role: AgentRole) -> Any:
        """
        Get appropriate memory system for agent role.
        
        Args:
            agent_role: The agent role requesting memory
            
        Returns:
            Appropriate memory system for the agent
        """
        # Map agent roles to appropriate memory systems
        memory_mapping = {
            AgentRole.PLAYER_COORDINATOR: self.player_memory,
            AgentRole.TEAM_ADMINISTRATOR: self.team_member_memory,
            AgentRole.SQUAD_SELECTOR: self.player_memory,  # Also needs player data
            AgentRole.MESSAGE_PROCESSOR: self.short_term_memory,
            AgentRole.HELP_ASSISTANT: self.short_term_memory,
        }
        
        memory_system = memory_mapping.get(agent_role, self.short_term_memory)
        
        # In CrewAI 0.157.0, memory objects are used for agent context
        # If memory system is available, return it; otherwise use local cache
        if memory_system is not None:
            return memory_system
        else:
            logger.warning(f"⚠️ No memory system available for {agent_role.value}, using local cache")
            return self._get_local_memory_proxy()
    
    def get_memory_for_entity(self, entity_type: EntityType) -> Any:
        """
        Get memory system for specific entity type.
        
        Args:
            entity_type: The entity type
            
        Returns:
            Appropriate memory system for the entity
        """
        entity_memory_mapping = {
            EntityType.PLAYER: self.player_memory,
            EntityType.TEAM_MEMBER: self.team_member_memory,
            EntityType.TEAM: self.team_memory,
        }
        
        memory_system = entity_memory_mapping.get(entity_type, self.short_term_memory)
        
        if memory_system is None:
            logger.warning(f"⚠️ No memory system available for {entity_type.value}, using local cache")
            return self._get_local_memory_proxy()
        
        return memory_system
    
    def store_player_memory(self, player_id: str, key: str, value: Any, ttl: Optional[timedelta] = None, metadata: Dict[str, Any] = None):
        """
        Store memory for a specific player.
        
        Args:
            player_id: The player ID
            key: Memory key
            value: Memory value
            ttl: Time to live (optional)
            metadata: Additional metadata
        """
        try:
            # Store in local cache for fast access (primary storage)
            entry = MemoryEntry(
                key=key,
                value=value,
                entity_type=EntityType.PLAYER,
                entity_id=player_id,
                timestamp=datetime.now(),
                ttl=ttl,
                metadata=metadata or {}
            )
            
            cache_key = f"player:{player_id}:{key}"
            self._local_cache[cache_key] = entry
            
            # Note: CrewAI memory is now used for agent context, not direct storage
            logger.debug(f"💾 Stored player memory: {player_id}:{key}")
            
        except Exception as e:
            logger.error(f"❌ Failed to store player memory: {e}")
    
    def get_player_memory(self, player_id: str, key: str) -> Optional[Any]:
        """
        Retrieve memory for a specific player.
        
        Args:
            player_id: The player ID
            key: Memory key
            
        Returns:
            Memory value if found, None otherwise
        """
        try:
            # Check local cache (primary storage)
            cache_key = f"player:{player_id}:{key}"
            if cache_key in self._local_cache:
                entry = self._local_cache[cache_key]
                if not entry.is_expired():
                    return entry.value
                else:
                    # Remove expired entry
                    del self._local_cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve player memory: {e}")
            return None
    
    def store_team_member_memory(self, team_member_id: str, key: str, value: Any, ttl: Optional[timedelta] = None, metadata: Dict[str, Any] = None):
        """
        Store memory for a specific team member.
        
        Args:
            team_member_id: The team member ID
            key: Memory key
            value: Memory value
            ttl: Time to live (optional)
            metadata: Additional metadata
        """
        try:
            # Store in local cache for fast access (primary storage)
            entry = MemoryEntry(
                key=key,
                value=value,
                entity_type=EntityType.TEAM_MEMBER,
                entity_id=team_member_id,
                timestamp=datetime.now(),
                ttl=ttl,
                metadata=metadata or {}
            )
            
            cache_key = f"team_member:{team_member_id}:{key}"
            self._local_cache[cache_key] = entry
            
            logger.debug(f"💾 Stored team member memory: {team_member_id}:{key}")
            
        except Exception as e:
            logger.error(f"❌ Failed to store team member memory: {e}")
    
    def get_team_member_memory(self, team_member_id: str, key: str) -> Optional[Any]:
        """
        Retrieve memory for a specific team member.
        
        Args:
            team_member_id: The team member ID
            key: Memory key
            
        Returns:
            Memory value if found, None otherwise
        """
        try:
            # Check local cache (primary storage)
            cache_key = f"team_member:{team_member_id}:{key}"
            if cache_key in self._local_cache:
                entry = self._local_cache[cache_key]
                if not entry.is_expired():
                    return entry.value
                else:
                    # Remove expired entry
                    del self._local_cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve team member memory: {e}")
            return None
    
    def store_session_memory(self, session_id: str, key: str, value: Any, ttl: Optional[timedelta] = None):
        """
        Store session-based memory (short-term).
        
        Args:
            session_id: The session ID
            key: Memory key
            value: Memory value
            ttl: Time to live (optional)
        """
        try:
            # Store in local cache (primary storage)
            entry = MemoryEntry(
                key=key,
                value=value,
                entity_type=EntityType.NEITHER,
                entity_id=session_id,
                timestamp=datetime.now(),
                ttl=ttl or timedelta(hours=1)  # Default 1 hour TTL for session memory
            )
            
            cache_key = f"session:{session_id}:{key}"
            self._local_cache[cache_key] = entry
            
            logger.debug(f"💾 Stored session memory: {session_id}:{key}")
            
        except Exception as e:
            logger.error(f"❌ Failed to store session memory: {e}")
    
    def get_session_memory(self, session_id: str, key: str) -> Optional[Any]:
        """
        Retrieve session-based memory.
        
        Args:
            session_id: The session ID
            key: Memory key
            
        Returns:
            Memory value if found, None otherwise
        """
        try:
            # Check local cache (primary storage)
            cache_key = f"session:{session_id}:{key}"
            if cache_key in self._local_cache:
                entry = self._local_cache[cache_key]
                if not entry.is_expired():
                    return entry.value
                else:
                    # Remove expired entry
                    del self._local_cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve session memory: {e}")
            return None
    
    def store_long_term_memory(self, key: str, value: Any, metadata: Dict[str, Any] = None):
        """
        Store long-term memory (persistent).
        
        Args:
            key: Memory key
            value: Memory value
            metadata: Additional metadata
        """
        try:
            # Store in local cache (primary storage)
            entry = MemoryEntry(
                key=key,
                value=value,
                entity_type=EntityType.NEITHER,
                entity_id="system",
                timestamp=datetime.now(),
                ttl=None,  # No TTL for long-term memory
                metadata=metadata or {}
            )
            
            cache_key = f"long_term:{key}"
            self._local_cache[cache_key] = entry
            
            logger.debug(f"💾 Stored long-term memory: {key}")
            
        except Exception as e:
            logger.error(f"❌ Failed to store long-term memory: {e}")
    
    def get_long_term_memory(self, key: str) -> Optional[Any]:
        """
        Retrieve long-term memory.
        
        Args:
            key: Memory key
            
        Returns:
            Memory value if found, None otherwise
        """
        try:
            # Check local cache (primary storage)
            cache_key = f"long_term:{key}"
            if cache_key in self._local_cache:
                entry = self._local_cache[cache_key]
                return entry.value
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve long-term memory: {e}")
            return None
    
    def cleanup_expired_memory(self):
        """Clean up expired memory entries from local cache."""
        try:
            expired_keys = []
            for key, entry in self._local_cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._local_cache[key]
            
            if expired_keys:
                logger.info(f"🧹 Cleaned up {len(expired_keys)} expired memory entries")
                
        except Exception as e:
            logger.error(f"❌ Failed to cleanup expired memory: {e}")
    
    def _get_local_memory_proxy(self):
        """Get a proxy object that mimics CrewAI memory interface for local cache."""
        class LocalMemoryProxy:
            def __init__(self, manager):
                self.manager = manager
            
            def store(self, entity_id: str, key: str, value: Any):
                # Store in local cache
                entry = MemoryEntry(
                    key=key,
                    value=value,
                    entity_type=EntityType.NEITHER,
                    entity_id=entity_id,
                    timestamp=datetime.now()
                )
                cache_key = f"local:{entity_id}:{key}"
                self.manager._local_cache[cache_key] = entry
            
            def retrieve(self, entity_id: str, key: str) -> Optional[Any]:
                cache_key = f"local:{entity_id}:{key}"
                if cache_key in self.manager._local_cache:
                    entry = self.manager._local_cache[cache_key]
                    if not entry.is_expired():
                        return entry.value
                return None
        
        return LocalMemoryProxy(self)


# Global memory manager instance
_memory_manager: Optional[KICKAIMemoryManager] = None


def get_memory_manager() -> KICKAIMemoryManager:
    """Get the global memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = KICKAIMemoryManager()
    return _memory_manager


def initialize_memory_manager() -> KICKAIMemoryManager:
    """Initialize and return the memory manager."""
    return get_memory_manager()
