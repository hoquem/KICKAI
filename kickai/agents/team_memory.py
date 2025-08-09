"""
Team Memory for KICKAI Agents

This module provides memory functionality for agents to store and retrieve
information about team interactions and context, using only CrewAI's native memory.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TeamMemory:
    """
    CrewAI-only team memory implementation.
    Provides conversation history and user-specific memory without LangChain dependencies.
    """

    def __init__(self, team_id: str):
        self.team_id = team_id
        self._memory_store: Dict[str, Any] = {}
        self._conversation_history: List[Dict[str, Any]] = []
        self._user_memories: Dict[str, Dict[str, Any]] = {}
        logger.info(f"Initialized CrewAI-only team memory for {team_id}")

    def get_memory(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get memory for a specific user or team-wide memory.

        Args:
            user_id: Optional user ID for user-specific memory

        Returns:
            Memory dictionary with conversation history and context
        """
        if user_id:
            if user_id not in self._user_memories:
                self._user_memories[user_id] = {
                    "chat_history": [],
                    "context": {},
                    "last_interaction": None,
                }
            return self._user_memories[user_id]
        else:
            return {
                "chat_history": self._conversation_history,
                "context": self._memory_store,
                "last_interaction": None,
            }

    def add_conversation(
        self, user_id: str, input_text: str, output_text: str, context: Optional[Dict[str, Any]] = None
    ):
        """
        Add a conversation exchange to memory.

        Args:
            user_id: User ID for the conversation
            input_text: User input text
            output_text: System output text
            context: Optional context information
        """
        timestamp = datetime.utcnow()

        # Add to team-wide conversation history
        conversation_entry = {
            "user_id": user_id,
            "input": input_text,
            "output": output_text,
            "timestamp": timestamp,
            "context": context or {},
        }
        self._conversation_history.append(conversation_entry)

        # Add to user-specific memory
        if user_id not in self._user_memories:
            self._user_memories[user_id] = {
                "chat_history": [],
                "context": {},
                "last_interaction": None,
            }

        self._user_memories[user_id]["chat_history"].append(conversation_entry)
        self._user_memories[user_id]["last_interaction"] = timestamp

        # Update context
        if context:
            self._user_memories[user_id]["context"].update(context)

        logger.debug(f"Added conversation to memory for user {user_id}")

    def store_conversation(self, user_id: str, message: str, response: str, agent_role: str = None):
        """
        Store a conversation exchange in memory (alias for add_conversation).

        Args:
            user_id: User ID for the conversation
            message: User input message
            response: System response
            agent_role: Optional agent role that handled the conversation
        """
        context = {"agent_role": agent_role} if agent_role else None
        self.add_conversation(user_id, message, response, context)

    def get_conversation_history(
        self, user_id: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a user or team.

        Args:
            user_id: Optional user ID for user-specific history
            limit: Optional limit on number of conversations to return

        Returns:
            List of conversation entries
        """
        if user_id:
            history = self._user_memories.get(user_id, {}).get("chat_history", [])
        else:
            history = self._conversation_history

        if limit:
            history = history[-limit:]

        return history

    def clear_memory(self, user_id: Optional[str] = None):
        """
        Clear memory for a specific user or all memory.

        Args:
            user_id: Optional user ID to clear specific user memory
        """
        if user_id:
            if user_id in self._user_memories:
                del self._user_memories[user_id]
                logger.info(f"Cleared memory for user {user_id}")
        else:
            self._memory_store.clear()
            self._conversation_history.clear()
            self._user_memories.clear()
            logger.info(f"Cleared all team memory for {self.team_id}")

    def get_memory_summary(self) -> Dict[str, Any]:
        """
        Get a summary of memory usage.

        Returns:
            Dictionary with memory statistics
        """
        return {
            "team_id": self.team_id,
            "total_conversations": len(self._conversation_history),
            "unique_users": len(self._user_memories),
            "memory_store_size": len(self._memory_store),
            "last_interaction": max(
                [m.get("last_interaction") for m in self._user_memories.values()] + [None]
            )
            if self._user_memories
            else None,
        }

    def get_user_memory_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get user-specific memory context for agents.

        Args:
            user_id: User ID to get memory for

        Returns:
            Dictionary with memory context
        """
        if user_id in self._user_memories:
            memory_data = self._user_memories[user_id]
            conversations = memory_data.get("chat_history", [])

            # Format for CrewAI memory context
            return {
                "chat_history": conversations[-10:],  # Last 10 conversations
                "user_id": user_id,
                "team_id": self.team_id,
                "conversation_count": len(conversations),
                "context": memory_data.get("context", {}),
            }
        return {
            "chat_history": [],
            "user_id": user_id,
            "team_id": self.team_id,
            "conversation_count": 0,
            "context": {},
        }
