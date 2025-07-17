"""
Advanced Memory System - Main Orchestrator

This module provides the main memory system that orchestrates all components
following the single responsibility principle.
"""

import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field

from .storage.memory_storage import MemoryItem, MemoryType, MemoryPriority, InMemoryStorage
from .learning.preference_learner import PreferenceLearner
from .learning.pattern_recognizer import PatternRecognizer
from .context.conversation_context import ConversationContextManager
from .optimization.memory_cleanup import MemoryCleanup
from .optimization.performance_optimizer import PerformanceOptimizer

logger = logging.getLogger(__name__)


@dataclass
class UserPreference:
    """Represents a user preference."""
    user_id: str
    preference_type: str
    preference_value: Any
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)
    usage_count: int = 0
    last_used: float = field(default_factory=time.time)


@dataclass
class Pattern:
    """Represents a learned pattern."""
    id: str
    pattern_type: str
    pattern_data: Dict[str, Any]
    confidence: float = 1.0
    occurrence_count: int = 1
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)


class AdvancedMemorySystem:
    """
    Advanced memory system using modular components.
    
    This class orchestrates the memory management process using separate
    components for storage, learning, context management, and optimization.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the advanced memory system.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # Initialize components
        self.storage = InMemoryStorage()
        self.preference_learner = PreferenceLearner()
        self.pattern_recognizer = PatternRecognizer()
        self.context_manager = ConversationContextManager()
        self.memory_cleanup = MemoryCleanup()
        self.performance_optimizer = PerformanceOptimizer()
        
        # Memory type storage
        self.short_term_memories: Dict[str, MemoryItem] = {}
        self.long_term_memories: Dict[str, MemoryItem] = {}
        self.episodic_memories: Dict[str, MemoryItem] = {}
        self.semantic_memories: Dict[str, MemoryItem] = {}
        
        # User preferences and patterns
        self.user_preferences: Dict[str, Dict[str, UserPreference]] = {}
        self.patterns: Dict[str, Pattern] = {}
        
        logger.info("AdvancedMemorySystem initialized with modular components")
    
    def store_memory(self, content: Any, memory_type: MemoryType, 
                    user_id: Optional[str] = None, team_id: Optional[str] = None,
                    chat_id: Optional[str] = None, priority: MemoryPriority = MemoryPriority.MEDIUM,
                    context: Optional[Dict[str, Any]] = None, tags: Optional[Set[str]] = None,
                    importance: Optional[float] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store a memory item using the storage component.
        
        Args:
            content: Memory content
            memory_type: Type of memory
            user_id: User ID
            team_id: Team ID
            chat_id: Chat ID
            priority: Memory priority
            context: Additional context
            tags: Memory tags
            importance: Memory importance
            metadata: Additional metadata
            
        Returns:
            Memory ID
        """
        memory_id = str(uuid.uuid4())
        
        memory_item = MemoryItem(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            priority=priority,
            timestamp=time.time(),
            user_id=user_id,
            team_id=team_id,
            chat_id=chat_id,
            context=context or {},
            tags=tags or set(),
            importance=importance or 0.5,
            metadata=metadata or {}
        )
        
        # Store using appropriate storage method
        if memory_type == MemoryType.SHORT_TERM:
            self._store_in_short_term(memory_item)
        elif memory_type == MemoryType.LONG_TERM:
            self._store_in_long_term(memory_item)
        elif memory_type == MemoryType.EPISODIC:
            self._store_in_episodic(memory_item)
        elif memory_type == MemoryType.SEMANTIC:
            self._store_in_semantic(memory_item)
        
        # Also store in main storage
        self.storage.store(memory_item)
        
        logger.debug(f"Stored memory {memory_id} of type {memory_type.value}")
        return memory_id
    
    def retrieve_memory(self, query: Any, memory_type: Optional[MemoryType] = None,
                       user_id: Optional[str] = None, team_id: Optional[str] = None,
                       limit: int = 10, memory_types: Optional[List[MemoryType]] = None,
                       min_importance: Optional[float] = None) -> List[MemoryItem]:
        """
        Retrieve memory items using the storage component.
        
        Args:
            query: Search query
            memory_type: Specific memory type to search
            user_id: User ID filter
            team_id: Team ID filter
            limit: Maximum number of results
            memory_types: List of memory types to search
            min_importance: Minimum importance threshold
            
        Returns:
            List of memory items
        """
        # Use storage component for retrieval
        results = self.storage.retrieve(str(query), memory_type, limit)
        
        # Apply additional filters
        filtered_results = []
        for memory in results:
            # Filter by user ID
            if user_id and memory.user_id != user_id:
                continue
            
            # Filter by team ID
            if team_id and memory.team_id != team_id:
                continue
            
            # Filter by memory types
            if memory_types and memory.memory_type not in memory_types:
                continue
            
            # Filter by importance
            if min_importance and memory.importance < min_importance:
                continue
            
            filtered_results.append(memory)
        
        # Update access statistics
        for memory in filtered_results:
            memory.access_count += 1
            memory.last_accessed = time.time()
        
        return filtered_results[:limit]
    
    def learn_user_preference(self, user_id: str, preference_type: str, 
                            preference_value: Any, confidence: float = 1.0) -> None:
        """Learn a user preference using the preference learner."""
        self.preference_learner.learn_preference(user_id, preference_type, preference_value, confidence)
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences using the preference learner."""
        return self.preference_learner.get_preferences(user_id)
    
    def learn_pattern(self, pattern_type: str, pattern_data: Dict[str, Any],
                     context: Optional[Dict[str, Any]] = None) -> str:
        """Learn a pattern using the pattern recognizer."""
        return self.pattern_recognizer.learn_pattern(pattern_type, pattern_data, context)
    
    def get_relevant_patterns(self, context: Dict[str, Any], 
                            pattern_type: Optional[str] = None) -> List[Pattern]:
        """Get relevant patterns using the pattern recognizer."""
        return self.pattern_recognizer.get_relevant_patterns(context, pattern_type)
    
    def get_conversation_context(self, user_id: str, chat_id: str) -> Any:
        """Get conversation context using the context manager."""
        return self.context_manager.get_context(user_id, chat_id)
    
    def add_message_to_context(self, user_id: str, chat_id: str, 
                             message: Dict[str, Any]) -> None:
        """Add message to conversation context using the context manager."""
        self.context_manager.add_message(user_id, chat_id, message)
    
    def cleanup_memory(self) -> Dict[str, int]:
        """Clean up memory using the cleanup component."""
        return self.memory_cleanup.cleanup(self.storage)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        stats = {
            'total_memories': len(self.storage.memories),
            'short_term': len(self.short_term_memories),
            'long_term': len(self.long_term_memories),
            'episodic': len(self.episodic_memories),
            'semantic': len(self.semantic_memories),
            'user_preferences': sum(len(prefs) for prefs in self.user_preferences.values()),
            'patterns': len(self.patterns),
            'conversation_contexts': self.context_manager.get_context_count()
        }
        return stats
    
    def export_memory(self) -> Dict[str, Any]:
        """Export memory data for backup."""
        export_data = {
            'memories': [memory.to_dict() for memory in self.storage.memories.values()],
            'user_preferences': {
                user_id: {
                    pref_type: {
                        'preference_value': pref.preference_value,
                        'confidence': pref.confidence,
                        'timestamp': pref.timestamp,
                        'usage_count': pref.usage_count,
                        'last_used': pref.last_used
                    }
                    for pref_type, pref in prefs.items()
                }
                for user_id, prefs in self.user_preferences.items()
            },
            'patterns': {
                pattern_id: {
                    'pattern_type': pattern.pattern_type,
                    'pattern_data': pattern.pattern_data,
                    'confidence': pattern.confidence,
                    'occurrence_count': pattern.occurrence_count,
                    'first_seen': pattern.first_seen,
                    'last_seen': pattern.last_seen,
                    'context': pattern.context
                }
                for pattern_id, pattern in self.patterns.items()
            },
            'conversation_contexts': self.context_manager.export_contexts(),
            'export_timestamp': time.time()
        }
        return export_data
    
    def import_memory(self, data: Dict[str, Any]) -> None:
        """Import memory data from backup."""
        try:
            # Import memories
            for memory_data in data.get('memories', []):
                memory_item = MemoryItem.from_dict(memory_data)
                self.storage.store(memory_item)
            
            # Import user preferences
            for user_id, prefs_data in data.get('user_preferences', {}).items():
                self.user_preferences[user_id] = {}
                for pref_type, pref_data in prefs_data.items():
                    self.user_preferences[user_id][pref_type] = UserPreference(
                        user_id=user_id,
                        preference_type=pref_type,
                        **pref_data
                    )
            
            # Import patterns
            for pattern_id, pattern_data in data.get('patterns', {}).items():
                self.patterns[pattern_id] = Pattern(
                    id=pattern_id,
                    **pattern_data
                )
            
            # Import conversation contexts
            self.context_manager.import_contexts(data.get('conversation_contexts', {}))
            
            logger.info("Memory import completed successfully")
            
        except Exception as e:
            logger.error(f"Error importing memory: {e}")
            raise
    
    def _store_in_short_term(self, memory_item: MemoryItem) -> None:
        """Store in short-term memory."""
        self.short_term_memories[memory_item.id] = memory_item
    
    def _store_in_long_term(self, memory_item: MemoryItem) -> None:
        """Store in long-term memory."""
        self.long_term_memories[memory_item.id] = memory_item
    
    def _store_in_episodic(self, memory_item: MemoryItem) -> None:
        """Store in episodic memory."""
        self.episodic_memories[memory_item.id] = memory_item
    
    def _store_in_semantic(self, memory_item: MemoryItem) -> None:
        """Store in semantic memory."""
        self.semantic_memories[memory_item.id] = memory_item


# Global memory system instance
_memory_system_instance: Optional[AdvancedMemorySystem] = None


def get_memory_system(config: Optional[Dict[str, Any]] = None) -> AdvancedMemorySystem:
    """Get the global memory system instance."""
    global _memory_system_instance
    if _memory_system_instance is None:
        _memory_system_instance = AdvancedMemorySystem(config)
    return _memory_system_instance


def initialize_memory_system(config: Optional[Dict[str, Any]] = None) -> AdvancedMemorySystem:
    """Initialize the memory system."""
    global _memory_system_instance
    _memory_system_instance = AdvancedMemorySystem(config)
    return _memory_system_instance


def cleanup_memory_system() -> None:
    """Clean up the memory system."""
    global _memory_system_instance
    if _memory_system_instance:
        _memory_system_instance.cleanup_memory()
        _memory_system_instance = None 