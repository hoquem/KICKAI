from datetime import datetime
from typing import Any, Dict, Optional, List

from kickai.features.communication.domain.entities.message import Message
from kickai.features.communication.domain.repositories.message_repository_interface import (
    MessageRepositoryInterface,
)


class MessageService:
    """Service for handling messages in the communication domain."""

    def __init__(self, message_repository: MessageRepositoryInterface):
        self._repo = message_repository

    async def send_message(
        self,
        sender_id: str,
        recipient_id: str,
        content: str,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Send a message and return the message ID."""
        if not conversation_id:
            # Generate a conversation_id based on sender and recipient (simple default)
            conversation_id = f"{min(sender_id, recipient_id)}_{max(sender_id, recipient_id)}"
        message = Message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            conversation_id=conversation_id,
            content=content,
            metadata=metadata,
            created_at=datetime.now(),
            status="sent",
        )
        message_id = await self._repo.save(message._dict_)
        return message_id

    async def fetch_messages(self, conversation_id: str, limit: int = 50) -> List[Message]:
        """Fetch messages for a conversation."""
        raw_messages = await self._repo.get_by_conversation(conversation_id, limit)
        return [Message(**msg) for msg in raw_messages]
