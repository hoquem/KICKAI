"""
Communication Service for handling Telegram communication operations.
"""

from loguru import logger

from kickai.features.communication.infrastructure.telegram_bot_service import TelegramBotService


class CommunicationService:
    """Service for handling communication operations including Telegram messaging."""

    def __init__(self, telegram_bot_service: TelegramBotService | None = None):
        self.telegram_bot_service = telegram_bot_service

    def set_telegram_bot_service(self, telegram_bot_service: TelegramBotService):
        """Set the TelegramBotService after it's created."""
        self.telegram_bot_service = telegram_bot_service
        logger.info("✅ CommunicationService: TelegramBotService set")

    async def send_message(self, message: str, chat_type: str, team_id: str) -> bool:
        """
        Send a message to a specific chat type.

        Args:
            message: The message to send
            chat_type: The chat type ('main_chat' or 'leadership_chat')
            team_id: The team ID

        Returns:
            bool: True if message sent successfully, False otherwise
        """
        try:
            if not self.telegram_bot_service:
                logger.error("❌ TelegramBotService not available in CommunicationService")
                return False

            # Determine the chat ID based on chat type
            if chat_type == "main_chat":
                chat_id = self.telegram_bot_service.main_chat_id
            elif chat_type == "leadership_chat":
                chat_id = self.telegram_bot_service.leadership_chat_id
            else:
                logger.error(f"Invalid chat_type: {chat_type}")
                return False

            if not chat_id:
                logger.error(f"No chat_id configured for chat_type: {chat_type}")
                return False

            # Send the message using TelegramBotService
            await self.telegram_bot_service.send_message(chat_id, message)
            logger.info(f"✅ Message sent to {chat_type} (team_id: {team_id})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send message to {chat_type}: {e}")
            return False

    async def send_announcement(self, announcement: str, team_id: str) -> bool:
        """
        Send an announcement to the main chat.

        Args:
            announcement: The announcement message
            team_id: The team ID

        Returns:
            bool: True if announcement sent successfully, False otherwise
        """
        try:
            if not self.telegram_bot_service:
                logger.error("❌ TelegramBotService not available in CommunicationService")
                return False

            # Send announcement to main chat
            success = await self.send_message(announcement, "main_chat", team_id)
            if success:
                logger.info(f"✅ Announcement sent to team {team_id}")
            return success

        except Exception as e:
            logger.error(f"❌ Failed to send announcement to team {team_id}: {e}")
            return False

    async def send_poll(self, question: str, options: str, team_id: str) -> bool:
        """
        Send a poll to the main chat.

        Args:
            question: The poll question
            options: Comma-separated poll options
            team_id: The team ID

        Returns:
            bool: True if poll sent successfully, False otherwise
        """
        try:
            if not self.telegram_bot_service:
                logger.error("❌ TelegramBotService not available in CommunicationService")
                return False

            # Format the poll message
            poll_message = f"📊 **Poll**: {question}\n\n"
            option_list = [opt.strip() for opt in options.split(",")]

            for i, option in enumerate(option_list, 1):
                poll_message += f"{i}. {option}\n"

            poll_message += f"\nPlease respond with your choice (1-{len(option_list)})"

            # Send poll to main chat
            success = await self.send_message(poll_message, "main_chat", team_id)
            if success:
                logger.info(f"✅ Poll sent to team {team_id}")
            return success

        except Exception as e:
            logger.error(f"❌ Failed to send poll to team {team_id}: {e}")
            return False
