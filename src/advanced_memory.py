#!/usr/bin/env python3
"""
Advanced Memory System for KICKAI
Implements intelligent memory management with multiple memory types,
user preference learning, and pattern recognition.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """Types of memory in the system."""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    USER_PREFERENCES = "user_preferences"
    PATTERNS = "patterns"

@dataclass
class MemoryItem:
    """Represents a single memory item."""
    id: str
    type: MemoryType
    content: Dict[str, Any]
    timestamp: float
    user_id: Optional[str] = None
    chat_id: Optional[str] = None
    importance: float = 1.0
    access_count: int = 0
    last_accessed: float = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.timestamp
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data['type'] = self.type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """Create from dictionary."""
        data['type'] = MemoryType(data['type'])
        return cls(**data)

@dataclass
class UserPreference:
    """Represents user preferences learned from interactions."""
    user_id: str
    preference_type: str
    value: Any
    confidence: float
    last_updated: float
    usage_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreference':
        """Create from dictionary."""
        return cls(**data)

@dataclass
class Pattern:
    """Represents a recognized pattern in user interactions."""
    pattern_id: str
    pattern_type: str
    trigger_conditions: List[str]
    response_pattern: str
    success_rate: float
    usage_count: int
    last_used: float
    created_at: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pattern':
        """Create from dictionary."""
        return cls(**data)

class AdvancedMemorySystem:
    """
    Advanced memory system with multiple memory types and intelligent management.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the advanced memory system."""
        self.config = config or {}
        
        # Memory storage
        self.short_term_memory: Dict[str, MemoryItem] = {}
        self.long_term_memory: Dict[str, MemoryItem] = {}
        self.episodic_memory: Dict[str, MemoryItem] = {}
        self.semantic_memory: Dict[str, MemoryItem] = {}
        
        # User preferences and patterns
        self.user_preferences: Dict[str, List[UserPreference]] = defaultdict(list)
        self.patterns: Dict[str, Pattern] = {}
        
        # Configuration
        self.max_short_term_items = self.config.get('max_short_term_items', 100)
        self.max_long_term_items = self.config.get('max_long_term_items', 1000)
        self.max_episodic_items = self.config.get('max_episodic_items', 500)
        self.max_semantic_items = self.config.get('max_semantic_items', 200)
        
        # Memory retention settings
        self.short_term_retention_hours = self.config.get('short_term_retention_hours', 24)
        self.long_term_retention_days = self.config.get('long_term_retention_days', 30)
        
        # Pattern recognition settings
        self.min_pattern_confidence = self.config.get('min_pattern_confidence', 0.7)
        self.pattern_learning_enabled = self.config.get('pattern_learning_enabled', True)
        
        logger.info("✅ Advanced Memory System initialized")
        logger.info(f"   Short-term capacity: {self.max_short_term_items}")
        logger.info(f"   Long-term capacity: {self.max_long_term_items}")
        logger.info(f"   Pattern learning: {'enabled' if self.pattern_learning_enabled else 'disabled'}")
    
    def _generate_memory_id(self, content: Dict[str, Any], memory_type: MemoryType) -> str:
        """Generate a unique ID for a memory item."""
        content_str = json.dumps(content, sort_keys=True)
        hash_input = f"{memory_type.value}:{content_str}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def store_memory(self, 
                    content: Dict[str, Any], 
                    memory_type: MemoryType,
                    user_id: Optional[str] = None,
                    chat_id: Optional[str] = None,
                    importance: float = 1.0,
                    tags: Optional[List[str]] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store a memory item in the appropriate memory type.
        
        Args:
            content: The content to store
            memory_type: Type of memory to store in
            user_id: Optional user ID
            chat_id: Optional chat ID
            importance: Importance score (0.0 to 1.0)
            tags: Optional tags for categorization
            metadata: Optional metadata
            
        Returns:
            Memory item ID
        """
        memory_id = self._generate_memory_id(content, memory_type)
        timestamp = time.time()
        
        memory_item = MemoryItem(
            id=memory_id,
            type=memory_type,
            content=content,
            timestamp=timestamp,
            user_id=user_id,
            chat_id=chat_id,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Store in appropriate memory type
        if memory_type == MemoryType.SHORT_TERM:
            self._store_short_term(memory_item)
        elif memory_type == MemoryType.LONG_TERM:
            self._store_long_term(memory_item)
        elif memory_type == MemoryType.EPISODIC:
            self._store_episodic(memory_item)
        elif memory_type == MemoryType.SEMANTIC:
            self._store_semantic(memory_item)
        
        logger.debug(f"Stored {memory_type.value} memory: {memory_id}")
        return memory_id
    
    def _store_short_term(self, memory_item: MemoryItem):
        """Store in short-term memory with capacity management."""
        self.short_term_memory[memory_item.id] = memory_item
        
        # Cleanup if over capacity
        if len(self.short_term_memory) > self.max_short_term_items:
            self._cleanup_short_term_memory()
    
    def _store_long_term(self, memory_item: MemoryItem):
        """Store in long-term memory with capacity management."""
        self.long_term_memory[memory_item.id] = memory_item
        
        # Cleanup if over capacity
        if len(self.long_term_memory) > self.max_long_term_items:
            self._cleanup_long_term_memory()
    
    def _store_episodic(self, memory_item: MemoryItem):
        """Store in episodic memory with capacity management."""
        if len(self.episodic_memory) >= self.max_episodic_items:
            self._cleanup_episodic_memory()
        
        self.episodic_memory[memory_item.id] = memory_item
    
    def _store_semantic(self, memory_item: MemoryItem):
        """Store in semantic memory with capacity management."""
        if len(self.semantic_memory) >= self.max_semantic_items:
            self._cleanup_semantic_memory()
        
        self.semantic_memory[memory_item.id] = memory_item
    
    def retrieve_memory(self, 
                       query: Dict[str, Any],
                       memory_types: Optional[List[MemoryType]] = None,
                       user_id: Optional[str] = None,
                       limit: int = 10,
                       min_importance: float = 0.0) -> List[MemoryItem]:
        """
        Retrieve relevant memories based on query.
        
        Args:
            query: Query to search for
            memory_types: Types of memory to search in
            user_id: Optional user ID filter
            limit: Maximum number of results
            min_importance: Minimum importance threshold
            
        Returns:
            List of relevant memory items
        """
        if memory_types is None:
            memory_types = [MemoryType.SHORT_TERM, MemoryType.LONG_TERM, 
                           MemoryType.EPISODIC, MemoryType.SEMANTIC]
        
        results = []
        
        for memory_type in memory_types:
            if memory_type == MemoryType.SHORT_TERM:
                results.extend(self._search_memory(self.short_term_memory, query, user_id, min_importance))
            elif memory_type == MemoryType.LONG_TERM:
                results.extend(self._search_memory(self.long_term_memory, query, user_id, min_importance))
            elif memory_type == MemoryType.EPISODIC:
                results.extend(self._search_memory(self.episodic_memory, query, user_id, min_importance))
            elif memory_type == MemoryType.SEMANTIC:
                results.extend(self._search_memory(self.semantic_memory, query, user_id, min_importance))
        
        # Sort by relevance and importance
        results.sort(key=lambda x: (x.importance, x.access_count), reverse=True)
        
        # Update access statistics
        for item in results[:limit]:
            item.access_count += 1
            item.last_accessed = time.time()
        
        return results[:limit]
    
    def _search_memory(self, 
                      memory_dict: Dict[str, MemoryItem],
                      query: Dict[str, Any],
                      user_id: Optional[str],
                      min_importance: float) -> List[MemoryItem]:
        """Search within a specific memory type."""
        results = []
        
        for memory_item in memory_dict.values():
            # Filter by importance
            if memory_item.importance < min_importance:
                continue
            
            # Filter by user if specified
            if user_id and memory_item.user_id != user_id:
                continue
            
            # Simple relevance scoring (can be enhanced with semantic search)
            relevance_score = self._calculate_relevance(memory_item, query)
            if relevance_score > 0.3:  # Threshold for relevance
                results.append(memory_item)
        
        return results
    
    def _calculate_relevance(self, memory_item: MemoryItem, query: Dict[str, Any]) -> float:
        """Calculate relevance score between memory item and query."""
        score = 0.0
        
        # Check for exact matches in content
        for key, value in query.items():
            if key in memory_item.content:
                if memory_item.content[key] == value:
                    score += 0.5
                elif isinstance(value, str) and isinstance(memory_item.content[key], str):
                    # Simple string similarity
                    if value.lower() in memory_item.content[key].lower():
                        score += 0.3
        
        # Check tag matches
        if 'tags' in query and memory_item.tags:
            for tag in query['tags']:
                if tag in memory_item.tags:
                    score += 0.2
        
        # Check for string matches in content values
        for key, value in query.items():
            if isinstance(value, str):
                for content_key, content_value in memory_item.content.items():
                    if isinstance(content_value, str) and value.lower() in content_value.lower():
                        score += 0.2
                        break
        
        # If no specific matches but query is empty or very general, give low score
        if not query or (len(query) == 1 and 'user_id' in query):
            score = 0.1
        
        return min(score, 1.0)
    
    def learn_user_preference(self, 
                            user_id: str,
                            preference_type: str,
                            value: Any,
                            confidence: float = 1.0):
        """
        Learn a user preference from interactions.
        
        Args:
            user_id: User ID
            preference_type: Type of preference (e.g., 'communication_style', 'response_length')
            value: Preference value
            confidence: Confidence in this preference (0.0 to 1.0)
        """
        if not self.pattern_learning_enabled:
            return
        
        # Check if preference already exists
        existing_pref = None
        for pref in self.user_preferences[user_id]:
            if pref.preference_type == preference_type:
                existing_pref = pref
                break
        
        if existing_pref:
            # Update existing preference
            existing_pref.value = value
            existing_pref.confidence = min(existing_pref.confidence + confidence, 1.0)
            existing_pref.last_updated = time.time()
            existing_pref.usage_count += 1
        else:
            # Create new preference
            new_pref = UserPreference(
                user_id=user_id,
                preference_type=preference_type,
                value=value,
                confidence=confidence,
                last_updated=time.time(),
                usage_count=1
            )
            self.user_preferences[user_id].append(new_pref)
        
        logger.debug(f"Learned preference for user {user_id}: {preference_type} = {value}")
    
    def get_user_preferences(self, user_id: str) -> List[UserPreference]:
        """Get all preferences for a user."""
        return self.user_preferences.get(user_id, [])
    
    def learn_pattern(self, 
                     pattern_type: str,
                     trigger_conditions: List[str],
                     response_pattern: str,
                     success: bool):
        """
        Learn a pattern from user interactions.
        
        Args:
            pattern_type: Type of pattern
            trigger_conditions: Conditions that trigger this pattern
            response_pattern: The response pattern
            success: Whether the pattern was successful
        """
        if not self.pattern_learning_enabled:
            return
        
        pattern_id = hashlib.md5(f"{pattern_type}:{json.dumps(trigger_conditions)}".encode()).hexdigest()
        
        if pattern_id in self.patterns:
            # Update existing pattern
            pattern = self.patterns[pattern_id]
            pattern.usage_count += 1
            pattern.last_used = time.time()
            
            # Update success rate
            if success:
                pattern.success_rate = (pattern.success_rate * (pattern.usage_count - 1) + 1) / pattern.usage_count
            else:
                pattern.success_rate = (pattern.success_rate * (pattern.usage_count - 1)) / pattern.usage_count
        else:
            # Create new pattern
            pattern = Pattern(
                pattern_id=pattern_id,
                pattern_type=pattern_type,
                trigger_conditions=trigger_conditions,
                response_pattern=response_pattern,
                success_rate=1.0 if success else 0.0,
                usage_count=1,
                last_used=time.time(),
                created_at=time.time()
            )
            self.patterns[pattern_id] = pattern
        
        logger.debug(f"Learned pattern: {pattern_type} (success rate: {pattern.success_rate:.2f})")
    
    def get_relevant_patterns(self, context: Dict[str, Any]) -> List[Pattern]:
        """Get patterns relevant to the current context."""
        relevant_patterns = []
        
        for pattern in self.patterns.values():
            if pattern.success_rate < self.min_pattern_confidence:
                continue
            
            # Check if pattern conditions match context
            if self._pattern_matches_context(pattern, context):
                relevant_patterns.append(pattern)
        
        # Sort by success rate and usage count
        relevant_patterns.sort(key=lambda x: (x.success_rate, x.usage_count), reverse=True)
        
        return relevant_patterns
    
    def _pattern_matches_context(self, pattern: Pattern, context: Dict[str, Any]) -> bool:
        """Check if pattern conditions match the current context."""
        context_str = str(context).lower()
        for condition in pattern.trigger_conditions:
            if condition.lower() not in context_str:
                return False
        return True
    
    def get_conversation_context(self, 
                                user_id: str,
                                chat_id: Optional[str] = None,
                                limit: int = 10) -> List[MemoryItem]:
        """Get conversation context for a user/chat."""
        query = {'user_id': user_id}
        if chat_id:
            query['chat_id'] = chat_id
        
        return self.retrieve_memory(
            query=query,
            memory_types=[MemoryType.SHORT_TERM, MemoryType.EPISODIC],
            user_id=user_id,
            limit=limit
        )
    
    def cleanup_memory(self):
        """Clean up old and low-importance memories."""
        self._cleanup_short_term_memory()
        self._cleanup_long_term_memory()
        self._cleanup_episodic_memory()
        self._cleanup_semantic_memory()
        self._cleanup_user_preferences()
        self._cleanup_patterns()
        
        logger.info("Memory cleanup completed")
    
    def _cleanup_short_term_memory(self):
        """Clean up short-term memory based on age and importance."""
        current_time = time.time()
        cutoff_time = current_time - (self.short_term_retention_hours * 3600)
        
        to_remove = []
        for memory_id, item in self.short_term_memory.items():
            if (item.timestamp < cutoff_time and item.importance < 0.5) or \
               (item.access_count == 0 and item.timestamp < cutoff_time - 3600):
                to_remove.append(memory_id)
        
        for memory_id in to_remove:
            del self.short_term_memory[memory_id]
        
        if to_remove:
            logger.debug(f"Cleaned up {len(to_remove)} short-term memories")
        
        # If still over capacity, remove lowest importance items
        if len(self.short_term_memory) > self.max_short_term_items:
            items = list(self.short_term_memory.items())
            items.sort(key=lambda x: (x[1].importance, x[1].access_count))
            
            to_remove = items[:len(items) - self.max_short_term_items]
            for memory_id, _ in to_remove:
                del self.short_term_memory[memory_id]
            
            logger.debug(f"Cleaned up {len(to_remove)} short-term memories due to capacity")
    
    def _cleanup_long_term_memory(self):
        """Clean up long-term memory based on importance and access patterns."""
        # Remove low-importance items if over capacity
        if len(self.long_term_memory) > self.max_long_term_items:
            items = list(self.long_term_memory.items())
            items.sort(key=lambda x: (x[1].importance, x[1].access_count))
            
            to_remove = items[:len(items) - self.max_long_term_items]
            for memory_id, _ in to_remove:
                del self.long_term_memory[memory_id]
            
            logger.debug(f"Cleaned up {len(to_remove)} long-term memories")
        
        # Also clean up old items
        current_time = time.time()
        cutoff_time = current_time - (self.long_term_retention_days * 24 * 3600)
        
        to_remove = []
        for memory_id, item in self.long_term_memory.items():
            if item.timestamp < cutoff_time and item.importance < 0.3:
                to_remove.append(memory_id)
        
        for memory_id in to_remove:
            del self.long_term_memory[memory_id]
        
        if to_remove:
            logger.debug(f"Cleaned up {len(to_remove)} old long-term memories")
    
    def _cleanup_episodic_memory(self):
        """Clean up episodic memory based on age and importance."""
        current_time = time.time()
        cutoff_time = current_time - (self.long_term_retention_days * 24 * 3600)
        
        to_remove = []
        for memory_id, item in self.episodic_memory.items():
            if item.timestamp < cutoff_time and item.importance < 0.3:
                to_remove.append(memory_id)
        
        for memory_id in to_remove:
            del self.episodic_memory[memory_id]
        
        if to_remove:
            logger.debug(f"Cleaned up {len(to_remove)} episodic memories")
    
    def _cleanup_semantic_memory(self):
        """Clean up semantic memory based on usage patterns."""
        # Remove rarely accessed semantic memories
        to_remove = []
        for memory_id, item in self.semantic_memory.items():
            if item.access_count < 2 and item.importance < 0.4:
                to_remove.append(memory_id)
        
        for memory_id in to_remove:
            del self.semantic_memory[memory_id]
        
        if to_remove:
            logger.debug(f"Cleaned up {len(to_remove)} semantic memories")
    
    def _cleanup_user_preferences(self):
        """Clean up old user preferences."""
        current_time = time.time()
        cutoff_time = current_time - (30 * 24 * 3600)  # 30 days
        
        for user_id in list(self.user_preferences.keys()):
            self.user_preferences[user_id] = [
                pref for pref in self.user_preferences[user_id]
                if pref.last_updated > cutoff_time or pref.usage_count > 5
            ]
            
            if not self.user_preferences[user_id]:
                del self.user_preferences[user_id]
    
    def _cleanup_patterns(self):
        """Clean up low-performing patterns."""
        to_remove = []
        for pattern_id, pattern in self.patterns.items():
            if pattern.success_rate < 0.3 and pattern.usage_count < 3:
                to_remove.append(pattern_id)
        
        for pattern_id in to_remove:
            del self.patterns[pattern_id]
        
        if to_remove:
            logger.debug(f"Cleaned up {len(to_remove)} low-performing patterns")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        return {
            'short_term_count': len(self.short_term_memory),
            'long_term_count': len(self.long_term_memory),
            'episodic_count': len(self.episodic_memory),
            'semantic_count': len(self.semantic_memory),
            'user_preferences_count': sum(len(prefs) for prefs in self.user_preferences.values()),
            'patterns_count': len(self.patterns),
            'total_memories': (len(self.short_term_memory) + len(self.long_term_memory) + 
                              len(self.episodic_memory) + len(self.semantic_memory))
        }
    
    def export_memory(self) -> Dict[str, Any]:
        """Export all memory data for persistence."""
        return {
            'short_term_memory': {k: v.to_dict() for k, v in self.short_term_memory.items()},
            'long_term_memory': {k: v.to_dict() for k, v in self.long_term_memory.items()},
            'episodic_memory': {k: v.to_dict() for k, v in self.episodic_memory.items()},
            'semantic_memory': {k: v.to_dict() for k, v in self.semantic_memory.items()},
            'user_preferences': {k: [p.to_dict() for p in v] for k, v in self.user_preferences.items()},
            'patterns': {k: v.to_dict() for k, v in self.patterns.items()},
            'config': self.config
        }
    
    def import_memory(self, data: Dict[str, Any]):
        """Import memory data from persistence."""
        # Import memories
        self.short_term_memory = {k: MemoryItem.from_dict(v) for k, v in data.get('short_term_memory', {}).items()}
        self.long_term_memory = {k: MemoryItem.from_dict(v) for k, v in data.get('long_term_memory', {}).items()}
        self.episodic_memory = {k: MemoryItem.from_dict(v) for k, v in data.get('episodic_memory', {}).items()}
        self.semantic_memory = {k: MemoryItem.from_dict(v) for k, v in data.get('semantic_memory', {}).items()}
        
        # Import user preferences
        self.user_preferences = defaultdict(list)
        for k, v in data.get('user_preferences', {}).items():
            self.user_preferences[k] = [UserPreference.from_dict(p) for p in v]
        
        # Import patterns
        self.patterns = {k: Pattern.from_dict(v) for k, v in data.get('patterns', {}).items()}
        
        # Import config
        if 'config' in data:
            self.config.update(data['config'])
        
        logger.info("Memory system data imported successfully") 