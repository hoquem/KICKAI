from abc import ABC, abstractmethod
from typing import Any, Union


class MessageRepositoryInterface(ABC):
    @abstractmethod
    async def save(self, message: dict[str, Any]) -> str:
        """Persist a message and return its ID."""
        pass

    @abstractmethod
    async def get_by_id(self, message_id: str) -> Union[dict[str, Any], None]:
        """Fetch a message by its ID."""
        pass

    @abstractmethod
    async def get_by_conversation(self, conversation_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """Fetch messages for a conversation."""
        pass

    @abstractmethod
    async def list_for_user(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """List messages for a user (sent or received)."""
        pass
