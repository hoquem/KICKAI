#!/usr/bin/env python3
"""
Context Manager

This module provides context management functionality for user interactions.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class UserContext:
    """User context information."""

    user_id: str
    team_id: Optional[str] = None
    chat_id: Optional[str] = None
    username: Optional[str] = None
    message_text: Optional[str] = None
    is_registered_player: bool = False
    is_leadership_chat: bool = False
    user_role: str = "player"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextManager:
    """Manages user context information."""

    def __init__(self):
        self.contexts: Dict[str, UserContext] = {}
        logger.info("ContextManager initialized")

    async def get_user_context(self, user_id: str) -> Optional[UserContext]:
        """Get user context by user ID."""
        return self.contexts.get(user_id)

    async def create_user_context(
        self,
        user_id: str,
        team_id: Optional[str] = None,
        chat_id: Optional[str] = None,
        username: Optional[str] = None,
        message_text: Optional[str] = None,
    ) -> UserContext:
        """Create a new user context."""
        # Determine if this is a leadership chat based on chat ID pattern
        is_leadership_chat = self._is_leadership_chat(chat_id)

        context = UserContext(
            user_id=user_id,
            team_id=team_id,
            chat_id=chat_id,
            username=username,
            message_text=message_text,
            is_leadership_chat=is_leadership_chat,
        )

        self.contexts[user_id] = context
        return context

    def _is_leadership_chat(self, chat_id: Optional[str]) -> bool:
        """Determine if a chat is a leadership chat based on chat ID pattern."""
        if not chat_id:
            return False

        # Leadership chats typically have specific patterns
        # This is a simplified implementation - in practice, you'd check against
        # a database of known leadership chat IDs or use a more sophisticated pattern
        leadership_indicators = [
            "leadership" in chat_id.lower(),
            "admin" in chat_id.lower(),
            "management" in chat_id.lower(),
        ]

        return any(leadership_indicators)

    async def update_user_context(self, user_id: str, **kwargs) -> Optional[UserContext]:
        """Update user context."""
        if user_id not in self.contexts:
            return None

        context = self.contexts[user_id]
        for key, value in kwargs.items():
            if hasattr(context, key):
                setattr(context, key, value)

        return context

    async def clear_user_context(self, user_id: str) -> bool:
        """Clear user context."""
        if user_id in self.contexts:
            del self.contexts[user_id]
            return True
        return False

    def get_all_contexts(self) -> Dict[str, UserContext]:
        """Get all user contexts."""
        return self.contexts.copy()


# Global context manager instance
_context_manager_instance: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    """Get the global context manager instance."""
    global _context_manager_instance
    if _context_manager_instance is None:
        _context_manager_instance = ContextManager()
    return _context_manager_instance
