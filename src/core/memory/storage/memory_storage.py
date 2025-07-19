"""
Memory Storage

This module provides memory storage implementations.
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict

logger = logging.getLogger(__name__)


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
    content: Any
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
    importance: float = 0.5
    type: Optional[MemoryType] = None
    
    def __post_init__(self):
        """Set type field for backward compatibility."""
        if self.type is None:
            self.type = self.memory_type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = {
            'id': self.id,
            'content': self.content,
            'memory_type': self.memory_type.value,
            'priority': self.priority.value,
            'timestamp': self.timestamp,
            'user_id': self.user_id,
            'team_id': self.team_id,
            'chat_id': self.chat_id,
            'context': self.context,
            'tags': list(self.tags),
            'access_count': self.access_count,
            'last_accessed': self.last_accessed,
            'metadata': self.metadata,
            'importance': self.importance
        }
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """Create from dictionary."""
        data['tags'] = set(data.get('tags', []))
        data['memory_type'] = MemoryType(data['memory_type'])
        data['priority'] = MemoryPriority(data['priority'])
        return cls(**data)


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
            if isinstance(memory.content, str):
                words = memory.content.lower().split()
            else:
                words = str(memory.content).lower().split()
            
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
        
        # Calculate word overlap
        overlap = len(set(query_words) & set(content_words))
        total_query_words = len(query_words)
        
        if total_query_words == 0:
            return 0.0
        
        # Base score from word overlap
        base_score = overlap / total_query_words
        
        # Boost score based on recency and importance
        time_factor = 1.0 / (1.0 + (time.time() - memory.timestamp) / 3600)  # Decay over hours
        importance_factor = memory.importance
        
        final_score = base_score * time_factor * importance_factor
        
        return final_score 


class UserPreference:
    """Stub for UserPreference. Replace with real implementation as needed."""
    def __init__(self, *args, **kwargs):
        pass 


class Pattern:
    """Stub for Pattern. Replace with real implementation as needed."""
    def __init__(self, *args, **kwargs):
        pass 