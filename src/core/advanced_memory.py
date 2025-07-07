#!/usr/bin/env python3
"""
Advanced Memory System for KICKAI

This module implements a sophisticated memory management system that supports:
- Multiple memory types (short-term, long-term, episodic, semantic)
- User preference learning and storage
- Pattern recognition and learning
- Conversation context management
- Memory persistence and export/import
- Performance optimization and cleanup

The system is designed to enhance agent effectiveness by providing rich context
and learning capabilities.
"""

import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class MemoryType(Enum):
    """Types of memory supported by the system."""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class MemoryPriority(Enum):
    """Priority levels for memory storage."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class MemoryItem:
    """Represents a single memory item."""
    id: str
    content: Any  # Changed from str to Any to support dict content
    memory_type: MemoryType
    priority: MemoryPriority
    timestamp: float
    user_id: Optional[str] = None
    team_id: Optional[str] = None
    chat_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5  # Added importance field for test compatibility
    type: Optional[MemoryType] = None  # Added type field for test compatibility
    
    def __post_init__(self):
        """Set type field for backward compatibility."""
        if self.type is None:
            self.type = self.memory_type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['tags'] = list(self.tags)
        data['memory_type'] = self.memory_type.value
        data['priority'] = self.priority.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """Create from dictionary."""
        data['tags'] = set(data.get('tags', []))
        data['memory_type'] = MemoryType(data['memory_type'])
        data['priority'] = MemoryPriority(data['priority'])
        return cls(**data)


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


@dataclass
class ConversationContext:
    """Represents conversation context."""
    user_id: str
    chat_id: str
    team_id: Optional[str] = None
    messages: List[Dict[str, Any]] = field(default_factory=list)
    context_data: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    max_messages: int = 50


# ============================================================================
# MEMORY STORAGE INTERFACES
# ============================================================================

class MemoryStorage(ABC):
    """Abstract base class for memory storage implementations."""
    
    @abstractmethod
    def store(self, memory_item: MemoryItem) -> None:
        """Store a memory item."""
        pass
    
    @abstractmethod
    def retrieve(self, query: str, memory_type: Optional[MemoryType] = None, 
                limit: int = 10) -> List[MemoryItem]:
        """Retrieve memory items based on query."""
        pass
    
    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Delete a memory item."""
        pass
    
    @abstractmethod
    def cleanup(self, max_age_hours: int = 24) -> int:
        """Clean up old memory items."""
        pass


class InMemoryStorage(MemoryStorage):
    """In-memory storage implementation."""
    
    def __init__(self):
        self.memories: Dict[str, MemoryItem] = {}
        self.index: Dict[str, Set[str]] = defaultdict(set)
    
    def store(self, memory_item: MemoryItem) -> None:
        """Store a memory item."""
        self.memories[memory_item.id] = memory_item
        
        # Index by content words - handle both string and dict content
        if isinstance(memory_item.content, str):
            content_text = memory_item.content
        elif isinstance(memory_item.content, dict):
            # Convert dict to string for indexing
            content_text = json.dumps(memory_item.content, sort_keys=True)
        else:
            content_text = str(memory_item.content)
        
        words = content_text.lower().split()
        for word in words:
            if len(word) > 2:  # Skip very short words
                self.index[word].add(memory_item.id)
    
    def retrieve(self, query: str, memory_type: Optional[MemoryType] = None, 
                limit: int = 10) -> List[MemoryItem]:
        """Retrieve memory items based on query."""
        query_words = query.lower().split()
        candidate_ids = set()
        
        # Find memories containing query words
        for word in query_words:
            if word in self.index:
                candidate_ids.update(self.index[word])
        
        # Filter and score results
        results = []
        for memory_id in candidate_ids:
            if memory_id in self.memories:
                memory = self.memories[memory_id]
                
                # Filter by memory type if specified
                if memory_type and memory.memory_type != memory_type:
                    continue
                
                # Calculate relevance score
                score = self._calculate_relevance_score(memory, query_words)
                results.append((memory, score))
        
        # Sort by score and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, _ in results[:limit]]
    
    def delete(self, memory_id: str) -> bool:
        """Delete a memory item."""
        if memory_id in self.memories:
            memory = self.memories[memory_id]
            
            # Remove from index
            words = memory.content.lower().split()
            for word in words:
                if len(word) > 2 and memory_id in self.index[word]:
                    self.index[word].remove(memory_id)
            
            del self.memories[memory_id]
            return True
        return False
    
    def cleanup(self, max_age_hours: int = 24) -> int:
        """Clean up old memory items."""
        cutoff_time = time.time() - (max_age_hours * 3600)
        deleted_count = 0
        
        memory_ids = list(self.memories.keys())
        for memory_id in memory_ids:
            memory = self.memories[memory_id]
            if memory.timestamp < cutoff_time and memory.priority != MemoryPriority.CRITICAL:
                if self.delete(memory_id):
                    deleted_count += 1
        
        return deleted_count
    
    def _calculate_relevance_score(self, memory: MemoryItem, query_words: List[str]) -> float:
        """Calculate relevance score for a memory item."""
        # Handle different content types
        if isinstance(memory.content, str):
            content_words = memory.content.lower().split()
        elif isinstance(memory.content, dict):
            content_words = json.dumps(memory.content, sort_keys=True).lower().split()
        else:
            content_words = str(memory.content).lower().split()
        
        # Count matching words
        matches = sum(1 for word in query_words if word in content_words)
        
        # Base score from word matches
        score = matches / len(query_words) if query_words else 0
        
        # Boost by priority
        score *= memory.priority.value
        
        # Boost by recency (within last 24 hours)
        if time.time() - memory.timestamp < 86400:
            score *= 1.5
        
        # Boost by access frequency
        score *= (1 + memory.access_count * 0.1)
        
        return score


# ============================================================================
# MAIN MEMORY SYSTEM
# ============================================================================

class AdvancedMemorySystem:
    """Advanced memory system for KICKAI agents."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the memory system."""
        self.config = config or {}
        
        # Memory storage
        self.short_term_memory: Dict[str, MemoryItem] = {}
        self.long_term_memory: Dict[str, MemoryItem] = {}
        self.episodic_memory: Dict[str, MemoryItem] = {}
        self.semantic_memory: Dict[str, MemoryItem] = {}
        
        # User preferences
        self.user_preferences: Dict[str, Dict[str, UserPreference]] = defaultdict(dict)
        
        # Pattern learning
        self.patterns: Dict[str, Pattern] = {}
        
        # Conversation contexts
        self.conversation_contexts: Dict[str, ConversationContext] = {}
        
        # Configuration
        self.max_short_term_items = self.config.get('max_short_term_items', 100)
        self.max_long_term_items = self.config.get('max_long_term_items', 1000)
        self.max_episodic_items = self.config.get('max_episodic_items', 500)
        self.max_semantic_items = self.config.get('max_semantic_items', 200)
        
        self.pattern_learning_enabled = self.config.get('pattern_learning_enabled', True)
        self.preference_learning_enabled = self.config.get('preference_learning_enabled', True)
        
        # Storage implementation
        self.storage = InMemoryStorage()
        
        logger.info("✅ AdvancedMemorySystem initialized")
    
    def store_memory(self, content: Any, memory_type: MemoryType, 
                    user_id: Optional[str] = None, team_id: Optional[str] = None,
                    chat_id: Optional[str] = None, priority: MemoryPriority = MemoryPriority.MEDIUM,
                    context: Optional[Dict[str, Any]] = None, tags: Optional[Set[str]] = None,
                    importance: Optional[float] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store a new memory item."""
        memory_id = str(uuid.uuid4())
        
        # Convert priority to importance if not provided
        if importance is None:
            importance = priority.value / 4.0  # Normalize priority to 0-1 range
        
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
            importance=importance,
            metadata=metadata or {}
        )
        
        # Store in appropriate memory type
        if memory_type == MemoryType.SHORT_TERM:
            self._store_in_short_term(memory_item)
        elif memory_type == MemoryType.LONG_TERM:
            self._store_in_long_term(memory_item)
        elif memory_type == MemoryType.EPISODIC:
            self._store_in_episodic(memory_item)
        elif memory_type == MemoryType.SEMANTIC:
            self._store_in_semantic(memory_item)
        
        # Also store in general storage
        self.storage.store(memory_item)
        
        logger.debug(f"Stored memory: {memory_id} ({memory_type.value})")
        return memory_id
    
    def retrieve_memory(self, query: Any, memory_type: Optional[MemoryType] = None,
                       user_id: Optional[str] = None, team_id: Optional[str] = None,
                       limit: int = 10, memory_types: Optional[List[MemoryType]] = None,
                       min_importance: Optional[float] = None) -> List[MemoryItem]:
        """Retrieve memory items based on query."""
        # Handle different query types
        if isinstance(query, dict):
            # Convert dict query to string for search
            query_str = json.dumps(query, sort_keys=True)
        else:
            query_str = str(query)
        
        # Use memory_types if provided, otherwise use memory_type
        if memory_types:
            # Get results from each memory type
            all_results = []
            for mt in memory_types:
                results = self.storage.retrieve(query_str, mt, limit * 2)
                all_results.extend(results)
            results = all_results
        else:
            # Get results from storage
            results = self.storage.retrieve(query_str, memory_type, limit * 2)
        
        # Filter by user/team if specified
        if user_id or team_id:
            filtered_results = []
            for memory in results:
                if user_id and memory.user_id != user_id:
                    continue
                if team_id and memory.team_id != team_id:
                    continue
                filtered_results.append(memory)
            results = filtered_results
        
        # Filter by minimum importance if specified
        if min_importance is not None:
            filtered_results = []
            for memory in results:
                if memory.importance >= min_importance:
                    filtered_results.append(memory)
            results = filtered_results
        
        # Update access statistics
        for memory in results[:limit]:
            memory.access_count += 1
            memory.last_accessed = time.time()
        
        return results[:limit]
    
    def learn_user_preference(self, user_id: str, preference_type: str, 
                            preference_value: Any, confidence: float = 1.0) -> None:
        """Learn a user preference."""
        if not self.preference_learning_enabled:
            return
        
        preference_key = f"{preference_type}:{preference_value}"
        
        if preference_key in self.user_preferences[user_id]:
            # Update existing preference
            preference = self.user_preferences[user_id][preference_key]
            preference.usage_count += 1
            preference.last_used = time.time()
            preference.confidence = min(1.0, preference.confidence + 0.1)
        else:
            # Create new preference
            preference = UserPreference(
                user_id=user_id,
                preference_type=preference_type,
                preference_value=preference_value,
                confidence=confidence
            )
            self.user_preferences[user_id][preference_key] = preference
        
        logger.debug(f"Learned preference for user {user_id}: {preference_type} = {preference_value}")
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences."""
        if user_id not in self.user_preferences:
            return {}
        
        preferences = {}
        for preference in self.user_preferences[user_id].values():
            if preference.preference_type not in preferences:
                preferences[preference.preference_type] = []
            preferences[preference.preference_type].append({
                'value': preference.preference_value,
                'confidence': preference.confidence,
                'usage_count': preference.usage_count
            })
        
        return preferences
    
    def learn_pattern(self, pattern_type: str, pattern_data: Dict[str, Any],
                     context: Optional[Dict[str, Any]] = None) -> str:
        """Learn a new pattern."""
        if not self.pattern_learning_enabled:
            return ""
        
        # Create pattern hash for identification
        pattern_hash = hashlib.md5(
            json.dumps(pattern_data, sort_keys=True).encode()
        ).hexdigest()
        
        pattern_id = f"{pattern_type}:{pattern_hash}"
        
        if pattern_id in self.patterns:
            # Update existing pattern
            pattern = self.patterns[pattern_id]
            pattern.occurrence_count += 1
            pattern.last_seen = time.time()
            pattern.confidence = min(1.0, pattern.confidence + 0.05)
        else:
            # Create new pattern
            pattern = Pattern(
                id=pattern_id,
                pattern_type=pattern_type,
                pattern_data=pattern_data,
                context=context or {}
            )
            self.patterns[pattern_id] = pattern
        
        logger.debug(f"Learned pattern: {pattern_type} (occurrences: {pattern.occurrence_count})")
        return pattern_id
    
    def get_relevant_patterns(self, context: Dict[str, Any], 
                            pattern_type: Optional[str] = None) -> List[Pattern]:
        """Get patterns relevant to the given context."""
        relevant_patterns = []
        
        for pattern in self.patterns.values():
            if pattern_type and pattern.pattern_type != pattern_type:
                continue
            
            # Calculate relevance score
            relevance_score = self._calculate_pattern_relevance(pattern, context)
            if relevance_score > 0.3:  # Threshold for relevance
                relevant_patterns.append((pattern, relevance_score))
        
        # Sort by relevance and return
        relevant_patterns.sort(key=lambda x: x[1], reverse=True)
        return [pattern for pattern, _ in relevant_patterns[:10]]
    
    def get_conversation_context(self, user_id: str, chat_id: str) -> ConversationContext:
        """Get or create conversation context."""
        context_key = f"{user_id}:{chat_id}"
        
        if context_key not in self.conversation_contexts:
            self.conversation_contexts[context_key] = ConversationContext(
                user_id=user_id,
                chat_id=chat_id
            )
        
        return self.conversation_contexts[context_key]
    
    def add_message_to_context(self, user_id: str, chat_id: str, 
                             message: Dict[str, Any]) -> None:
        """Add a message to conversation context."""
        context = self.get_conversation_context(user_id, chat_id)
        context.messages.append(message)
        context.last_updated = time.time()
        
        # Limit message history
        if len(context.messages) > context.max_messages:
            context.messages = context.messages[-context.max_messages:]
    
    def cleanup_memory(self) -> Dict[str, int]:
        """Clean up old memory items."""
        cleanup_stats = {}
        
        # Clean up short-term memory (older than 1 hour)
        cutoff_time = time.time() - 3600
        deleted_count = 0
        for memory_id in list(self.short_term_memory.keys()):
            memory = self.short_term_memory[memory_id]
            if memory.timestamp < cutoff_time and memory.priority != MemoryPriority.CRITICAL:
                del self.short_term_memory[memory_id]
                deleted_count += 1
        cleanup_stats['short_term'] = deleted_count
        
        # Clean up conversation contexts (older than 24 hours)
        cutoff_time = time.time() - 86400
        deleted_count = 0
        for context_key in list(self.conversation_contexts.keys()):
            context = self.conversation_contexts[context_key]
            if context.last_updated < cutoff_time:
                del self.conversation_contexts[context_key]
                deleted_count += 1
        cleanup_stats['conversation_contexts'] = deleted_count
        
        # Clean up storage
        cleanup_stats['storage'] = self.storage.cleanup(24)
        
        logger.info(f"Memory cleanup completed: {cleanup_stats}")
        return cleanup_stats
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        return {
            'short_term_count': len(self.short_term_memory),
            'long_term_count': len(self.long_term_memory),
            'episodic_count': len(self.episodic_memory),
            'semantic_count': len(self.semantic_memory),
            'user_preferences_count': sum(len(prefs) for prefs in self.user_preferences.values()),
            'patterns_count': len(self.patterns),
            'conversation_contexts_count': len(self.conversation_contexts),
            'total_memories': len(self.short_term_memory) + len(self.long_term_memory) + 
                            len(self.episodic_memory) + len(self.semantic_memory)
        }
    
    def export_memory(self) -> Dict[str, Any]:
        """Export all memory data for persistence."""
        export_data = {
            'version': '1.0',
            'timestamp': time.time(),
            'config': self.config,
            'memories': {
                'short_term': [memory.to_dict() for memory in self.short_term_memory.values()],
                'long_term': [memory.to_dict() for memory in self.long_term_memory.values()],
                'episodic': [memory.to_dict() for memory in self.episodic_memory.values()],
                'semantic': [memory.to_dict() for memory in self.semantic_memory.values()]
            },
            'user_preferences': {
                user_id: {key: asdict(pref) for key, pref in user_prefs.items()}
                for user_id, user_prefs in self.user_preferences.items()
            },
            'patterns': {pattern_id: asdict(pattern) for pattern_id, pattern in self.patterns.items()},
            'conversation_contexts': {
                context_key: asdict(context) for context_key, context in self.conversation_contexts.items()
            }
        }
        
        return export_data
    
    def import_memory(self, data: Dict[str, Any]) -> None:
        """Import memory data from export."""
        if data.get('version') != '1.0':
            logger.warning("Importing memory data with unknown version")
        
        # Import memories
        for memory_type, memories in data.get('memories', {}).items():
            for memory_dict in memories:
                memory_item = MemoryItem.from_dict(memory_dict)
                if memory_type == 'short_term':
                    self.short_term_memory[memory_item.id] = memory_item
                elif memory_type == 'long_term':
                    self.long_term_memory[memory_item.id] = memory_item
                elif memory_type == 'episodic':
                    self.episodic_memory[memory_item.id] = memory_item
                elif memory_type == 'semantic':
                    self.semantic_memory[memory_item.id] = memory_item
        
        # Import user preferences
        for user_id, user_prefs in data.get('user_preferences', {}).items():
            for key, pref_dict in user_prefs.items():
                preference = UserPreference(**pref_dict)
                self.user_preferences[user_id][key] = preference
        
        # Import patterns
        for pattern_id, pattern_dict in data.get('patterns', {}).items():
            pattern = Pattern(**pattern_dict)
            self.patterns[pattern_id] = pattern
        
        # Import conversation contexts
        for context_key, context_dict in data.get('conversation_contexts', {}).items():
            context = ConversationContext(**context_dict)
            self.conversation_contexts[context_key] = context
        
        logger.info("Memory import completed successfully")
    
    def _store_in_short_term(self, memory_item: MemoryItem) -> None:
        """Store in short-term memory with size limit."""
        self.short_term_memory[memory_item.id] = memory_item
        
        # Enforce size limit
        if len(self.short_term_memory) > self.max_short_term_items:
            # Remove oldest, lowest priority items
            items = list(self.short_term_memory.items())
            items.sort(key=lambda x: (x[1].priority.value, x[1].timestamp))
            
            # Keep the best items
            self.short_term_memory = dict(items[-self.max_short_term_items:])
    
    def _store_in_long_term(self, memory_item: MemoryItem) -> None:
        """Store in long-term memory with size limit."""
        self.long_term_memory[memory_item.id] = memory_item
        
        if len(self.long_term_memory) > self.max_long_term_items:
            items = list(self.long_term_memory.items())
            items.sort(key=lambda x: (x[1].priority.value, x[1].timestamp))
            self.long_term_memory = dict(items[-self.max_long_term_items:])
    
    def _store_in_episodic(self, memory_item: MemoryItem) -> None:
        """Store in episodic memory with size limit."""
        self.episodic_memory[memory_item.id] = memory_item
        
        if len(self.episodic_memory) > self.max_episodic_items:
            items = list(self.episodic_memory.items())
            items.sort(key=lambda x: (x[1].priority.value, x[1].timestamp))
            self.episodic_memory = dict(items[-self.max_episodic_items:])
    
    def _store_in_semantic(self, memory_item: MemoryItem) -> None:
        """Store in semantic memory with size limit."""
        self.semantic_memory[memory_item.id] = memory_item
        
        if len(self.semantic_memory) > self.max_semantic_items:
            items = list(self.semantic_memory.items())
            items.sort(key=lambda x: (x[1].priority.value, x[1].timestamp))
            self.semantic_memory = dict(items[-self.max_semantic_items:])
    
    def _calculate_pattern_relevance(self, pattern: Pattern, context: Dict[str, Any]) -> float:
        """Calculate relevance score for a pattern."""
        score = 0.0
        
        # Check for context overlap
        for key, value in context.items():
            if key in pattern.context and pattern.context[key] == value:
                score += 0.2
        
        # Boost by confidence and occurrence count
        score *= pattern.confidence
        score *= min(1.0, pattern.occurrence_count / 10.0)
        
        # Boost by recency
        if time.time() - pattern.last_seen < 86400:  # Last 24 hours
            score *= 1.5
        
        return score


# ============================================================================
# GLOBAL INSTANCE AND CONVENIENCE FUNCTIONS
# ============================================================================

_global_memory_system: Optional[AdvancedMemorySystem] = None


def get_memory_system(config: Optional[Dict[str, Any]] = None) -> AdvancedMemorySystem:
    """Get the global memory system instance."""
    global _global_memory_system
    if _global_memory_system is None:
        _global_memory_system = AdvancedMemorySystem(config)
    return _global_memory_system


def initialize_memory_system(config: Optional[Dict[str, Any]] = None) -> AdvancedMemorySystem:
    """Initialize the global memory system."""
    global _global_memory_system
    _global_memory_system = AdvancedMemorySystem(config)
    return _global_memory_system


def cleanup_memory_system() -> None:
    """Clean up the global memory system."""
    global _global_memory_system
    if _global_memory_system:
        _global_memory_system.cleanup_memory()
        _global_memory_system = None 