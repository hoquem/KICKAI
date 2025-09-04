from abc import ABC, abstractmethod

from kickai.core.enums import ChatType
from kickai.features.shared.domain.models.help_models import HelpContent


class IHelpService(ABC):
    """Interface for help service operations."""

    @abstractmethod
    def generate_help_content(self, chat_type: ChatType, username: str) -> HelpContent:
        """
        Generate help content for a specific chat type.

        Args:
            chat_type: The chat type context
            username: User's name for personalization

        Returns:
            HelpContent with personalized help information
        """
        pass

    @abstractmethod
    def format_help_message(self, help_content: HelpContent) -> str:
        """
        Format help content into a displayable message.

        Args:
            help_content: The help content to format

        Returns:
            Formatted help message string
        """
        pass

    @abstractmethod
    def generate_welcome_message(self, username: str, chat_type: ChatType) -> str:
        """
        Generate a personalized welcome message.

        Args:
            username: User's name for personalization
            chat_type: The chat type context

        Returns:
            Personalized welcome message string
        """
        pass
