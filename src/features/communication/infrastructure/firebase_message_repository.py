"""
FirebaseMessageRepository for Communication.

Implements MessageRepositoryInterface using Firebase/Firestore as the backend.
"""
from typing import Any

from core.firestore_constants import COLLECTION_MESSAGES
from features.communication.domain.repositories.message_repository_interface import (
    MessageRepositoryInterface,
)


class FirebaseMessageRepository(MessageRepositoryInterface):
    """Repository for managing messages in Firebase/Firestore."""

    def __init__(self, firebase_client):
        self._client = firebase_client
        self._collection_name = COLLECTION_MESSAGES

    async def save(self, message: dict[str, Any]) -> str:
        """Persist a message and return its ID."""
        # TODO: Implement Firestore logic
        # For now, return a mock ID
        return message.get('id', 'mock_message_id')

    async def get_by_id(self, message_id: str) -> dict[str, Any] | None:
        """Fetch a message by its ID."""
        # TODO: Implement Firestore logic
        # For now, return None
        return None

    async def get_by_conversation(self, conversation_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """Fetch messages for a conversation."""
        # TODO: Implement Firestore logic
        # For now, return empty list
        return []

    async def get_by_user(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """Fetch messages for a user."""
        # TODO: Implement Firestore logic
        # For now, return empty list
        return []

    async def update(self, message_id: str, updates: dict[str, Any]) -> bool:
        """Update a message."""
        # TODO: Implement Firestore logic
        # For now, return True
        return True

    async def delete(self, message_id: str) -> bool:
        """Delete a message."""
        # TODO: Implement Firestore logic
        # For now, return True
        return True

    async def list_for_user(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """List messages for a user."""
        # TODO: Implement Firestore logic
        # For now, return empty list
        return []
