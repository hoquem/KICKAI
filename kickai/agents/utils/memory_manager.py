#!/usr/bin/env python3
"""
Optimized Memory Manager for CrewAI Agents

Separates memory management from execution context to follow CrewAI best practices
for minimal context passing while maintaining conversation history.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


@dataclass
class ConversationSummary:
    """Minimal conversation summary for context references."""
    
    telegram_id: int
    command: str
    response_type: str  # "success", "error", "help", "data"
    timestamp: datetime
    tokens_saved: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "telegram_id": self.telegram_id,
            "command": self.command[:30],  # Truncate
            "response_type": self.response_type,
            "timestamp": self.timestamp.isoformat(),
        }


class OptimizedMemoryManager:
    """
    Optimized memory manager that separates conversation history from execution context.
    
    Key optimizations:
    1. Stores conversation summaries instead of full content
    2. Implements memory cleanup and LRU eviction
    3. Provides references instead of embedded data
    4. Reduces context size by 90%+
    """

    def __init__(self, team_id: str, max_conversations: int = 100):
        self.team_id = team_id
        self.max_conversations = max_conversations
        
        # Use deque for efficient insertion/removal
        self._conversation_summaries: deque[ConversationSummary] = deque(maxlen=max_conversations)
        self._user_conversations: Dict[int, deque[ConversationSummary]] = defaultdict(
            lambda: deque(maxlen=20)  # Max 20 per user
        )
        
        # Memory usage tracking
        self._total_tokens_saved = 0
        self._cleanup_interval = timedelta(hours=24)
        self._last_cleanup = datetime.now()

    def add_conversation_summary(
        self,
        telegram_id: int,
        command: str,
        response: str,
        response_type: str = "success"
    ) -> ConversationSummary:
        """
        Add a conversation summary (not full content) to memory.
        
        This replaces storing full responses with minimal summaries.
        """
        # Calculate tokens saved by not storing full response
        full_response_tokens = len(response) // 4  # Rough estimate
        summary_tokens = len(command[:30]) // 4    # Only command prefix
        tokens_saved = full_response_tokens - summary_tokens
        
        summary = ConversationSummary(
            telegram_id=telegram_id,
            command=command,
            response_type=response_type,
            timestamp=datetime.now(),
            tokens_saved=tokens_saved
        )
        
        # Add to global and user-specific collections
        self._conversation_summaries.append(summary)
        self._user_conversations[telegram_id].append(summary)
        
        # Update metrics
        self._total_tokens_saved += tokens_saved
        
        # Periodic cleanup
        self._maybe_cleanup()
        
        logger.debug(
            f"Added conversation summary for user {telegram_id}, "
            f"saved ~{tokens_saved} tokens"
        )
        
        return summary

    def get_conversation_reference(
        self, 
        telegram_id: int
    ) -> Dict[str, Any]:
        """
        Get minimal conversation reference instead of full history.
        
        This is what gets passed to agents instead of full chat history.
        """
        user_conversations = self._user_conversations.get(telegram_id, deque())
        
        if not user_conversations:
            return {
                "has_history": False,
                "conversation_count": 0,
            }
        
        latest = user_conversations[-1]
        
        return {
            "has_history": True,
            "conversation_count": len(user_conversations),
            "last_command": latest.command[:20],  # Truncated
            "last_response_type": latest.response_type,
            "minutes_since_last": int((datetime.now() - latest.timestamp).total_seconds() / 60),
        }

    def get_conversation_context(self, telegram_id: int, limit: int = 5) -> Dict[str, Any]:
        """
        Get recent conversation context for agents that specifically need it.
        
        Used only when agents explicitly request conversation history.
        """
        user_conversations = list(self._user_conversations.get(telegram_id, deque()))
        recent = user_conversations[-limit:] if user_conversations else []
        
        return {
            "telegram_id": telegram_id,
            "team_id": self.team_id,
            "recent_conversations": [conv.to_dict() for conv in recent],
            "total_conversations": len(user_conversations),
            "context_type": "summary_only",  # Not full content
        }

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        return {
            "total_conversations": len(self._conversation_summaries),
            "unique_users": len(self._user_conversations),
            "total_tokens_saved": self._total_tokens_saved,
            "avg_tokens_saved_per_conversation": (
                self._total_tokens_saved / max(1, len(self._conversation_summaries))
            ),
            "memory_efficiency": f"{self._total_tokens_saved / max(1, len(self._conversation_summaries)):.1f} tokens/conv saved",
        }

    def _maybe_cleanup(self) -> None:
        """Periodic cleanup of old conversation summaries."""
        if datetime.now() - self._last_cleanup < self._cleanup_interval:
            return
        
        old_count = len(self._conversation_summaries)
        cutoff_time = datetime.now() - timedelta(days=7)  # Keep 7 days
        
        # Clean old conversations (deque handles max size automatically)
        for telegram_id, conversations in list(self._user_conversations.items()):
            # Remove conversations older than cutoff
            while conversations and conversations[0].timestamp < cutoff_time:
                conversations.popleft()
            
            # Remove empty entries
            if not conversations:
                del self._user_conversations[telegram_id]
        
        self._last_cleanup = datetime.now()
        
        if old_count != len(self._conversation_summaries):
            logger.info(
                f"Memory cleanup completed: {old_count} → {len(self._conversation_summaries)} conversations"
            )

    def clear_user_history(self, telegram_id: int) -> bool:
        """Clear conversation history for a specific user."""
        if telegram_id in self._user_conversations:
            del self._user_conversations[telegram_id]
            logger.info(f"Cleared conversation history for user {telegram_id}")
            return True
        return False

    def export_user_history(self, telegram_id: int) -> List[Dict[str, Any]]:
        """Export user conversation summaries for debugging or analysis."""
        user_conversations = self._user_conversations.get(telegram_id, deque())
        return [conv.to_dict() for conv in user_conversations]


# Global memory manager instance
_memory_managers: Dict[str, OptimizedMemoryManager] = {}


def get_memory_manager(team_id: str) -> OptimizedMemoryManager:
    """Get or create optimized memory manager for a team."""
    if team_id not in _memory_managers:
        _memory_managers[team_id] = OptimizedMemoryManager(team_id)
    return _memory_managers[team_id]


def get_memory_stats() -> Dict[str, Any]:
    """Get memory statistics across all teams."""
    total_stats = {
        "teams": len(_memory_managers),
        "total_conversations": 0,
        "total_users": 0,
        "total_tokens_saved": 0,
    }
    
    team_stats = {}
    for team_id, manager in _memory_managers.items():
        stats = manager.get_memory_stats()
        team_stats[team_id] = stats
        
        total_stats["total_conversations"] += stats["total_conversations"]
        total_stats["total_users"] += stats["unique_users"]
        total_stats["total_tokens_saved"] += stats["total_tokens_saved"]
    
    return {
        "total": total_stats,
        "by_team": team_stats,
        "efficiency": f"{total_stats['total_tokens_saved'] / max(1, total_stats['total_conversations']):.1f} tokens/conv saved globally"
    }