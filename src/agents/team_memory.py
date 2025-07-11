"""
Team Memory for KICKAI Agents

This module provides memory functionality for agents to store and retrieve
information about team interactions and context.
"""

import logging
from typing import Any, Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class TeamMemory:
    """Simple memory system for team agents."""
    
    def __init__(self, team_id: str):
        """
        Initialize team memory.
        
        Args:
            team_id: The team ID for this memory
        """
        self.team_id = team_id
        self._memory_store: Dict[str, Any] = {}
        self._conversation_history: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized team memory for {team_id}")
    
    def get_memory(self) -> Optional[Any]:
        """Get memory object for CrewAI agents."""
        # For now, return None to use default CrewAI memory
        # This can be enhanced later with custom memory implementations
        return None
    
    def store(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store a value in memory."""
        self._memory_store[key] = {
            'value': value,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
        logger.debug(f"Stored memory: {key}")
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value from memory."""
        if key in self._memory_store:
            return self._memory_store[key]['value']
        return None
    
    def add_conversation(self, user_id: str, message: str, response: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Add a conversation to memory."""
        conversation = {
            'user_id': user_id,
            'message': message,
            'response': response,
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        }
        self._conversation_history.append(conversation)
        logger.debug(f"Added conversation for user {user_id}")
    
    def get_conversation_history(self, user_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history."""
        if user_id:
            filtered_history = [conv for conv in self._conversation_history if conv['user_id'] == user_id]
            return filtered_history[-limit:]
        return self._conversation_history[-limit:]
    
    def clear(self) -> None:
        """Clear all memory."""
        self._memory_store.clear()
        self._conversation_history.clear()
        logger.info(f"Cleared memory for team {self.team_id}")
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of memory contents."""
        return {
            'team_id': self.team_id,
            'memory_entries': len(self._memory_store),
            'conversation_count': len(self._conversation_history),
            'memory_keys': list(self._memory_store.keys())
        } 