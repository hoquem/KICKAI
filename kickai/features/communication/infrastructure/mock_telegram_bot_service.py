#!/usr/bin/env python3
"""
Mock Telegram Bot Service

This module provides a mock implementation of TelegramBotService for isolated testing.
It simulates all Telegram bot functionality without requiring actual Telegram API calls.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from unittest.mock import Mock

from loguru import logger

from kickai.agents.user_flow_agent import AgentResponse, TelegramMessage
from kickai.core.enums import ChatType
from kickai.features.communication.domain.interfaces.telegram_bot_service_interface import (
    TelegramBotServiceInterface,
)


@dataclass
class MockUpdate:
    """Mock Telegram Update object for testing."""

    message: 'MockMessage'
    effective_message: 'MockMessage'
    effective_chat: 'MockChat'
    effective_user: 'MockUser'

    def __init__(self, message_text: str, chat_id: str, user_id: str, username: str = None):
        self.message = MockMessage(message_text, chat_id, user_id, username)
        self.effective_message = self.message
        self.effective_chat = MockChat(chat_id)
        self.effective_user = MockUser(user_id, username)


@dataclass
class MockMessage:
    """Mock Telegram Message object for testing."""

    text: str
    chat_id: str
    user_id: str
    username: str | None
    date: datetime = field(default_factory=datetime.now)

    async def reply_text(self, text: str, **kwargs):
        """Mock reply_text method."""
        logger.info(f"📤 Mock reply: {text}")
        return MockMessage(text, self.chat_id, "bot", "mock_bot")


@dataclass
class MockChat:
    """Mock Telegram Chat object for testing."""

    id: str
    type: str = "group"
    title: str = "Mock Chat"


@dataclass
class MockUser:
    """Mock Telegram User object for testing."""

    id: str
    username: str | None
    first_name: str = "Mock"
    last_name: str = "User"


@dataclass
class MockContext:
    """Mock Telegram Context object for testing."""

    bot: 'MockBot'

    def __init__(self):
        self.bot = MockBot()


class MockBot:
    """Mock Telegram Bot object for testing."""

    def __init__(self):
        self.username = "mock_bot"
        self.id = "123456789"
        self.first_name = "Mock"
        self.last_name = "Bot"

    async def get_me(self):
        """Mock get_me method."""
        return self

    async def send_message(self, chat_id: int | str, text: str, **kwargs):
        """Mock send_message method."""
        logger.info(f"📤 Mock bot send_message: {text}")
        return MockMessage(text, str(chat_id), "bot", "mock_bot")


class MockAgenticMessageRouter:
    """Mock implementation of AgenticMessageRouter for testing."""

    def __init__(self, team_id: str, crewai_system=None):
        self.team_id = team_id
        self.crewai_system = crewai_system
        self.routed_messages: list[TelegramMessage] = []
        self.responses: list[AgentResponse] = []

        # Pre-configured responses for common scenarios
        self._setup_mock_responses()

    def _setup_mock_responses(self):
        """Set up mock responses for common scenarios."""
        self.mock_responses = {
            "/start": AgentResponse(
                message="🎉 Welcome to KickAI! I'm here to help you manage your football team.",
                success=True
            ),
            "/help": AgentResponse(
                message="📋 Available commands:\n• /start - Get started\n• /myinfo - View your info\n• /list - List players\n• /status [phone] - Check status",
                success=True
            ),
            "/myinfo": AgentResponse(
                message="👤 Your Information:\n• Name: Test User\n• Phone: +1234567890\n• Position: Forward\n• Team: Test Team",
                success=True
            ),
            "/list": AgentResponse(
                message="📋 Active Players:\n1. John Doe - Forward\n2. Jane Smith - Midfielder\n3. Bob Wilson - Defender",
                success=True
            ),
            "hello": AgentResponse(
                message="👋 Hello! How can I help you today?",
                success=True
            ),
            "what's my phone number": AgentResponse(
                message="📱 Your phone number is +1234567890",
                success=True
            )
        }

    async def route_message(self, message: TelegramMessage) -> AgentResponse:
        """Mock message routing with predefined responses."""
        self.routed_messages.append(message)

        # Log the routing
        logger.info(f"🔄 MockAgenticMessageRouter: Routing message '{message.text}' from {message.username}")

        # Check for exact command matches first
        if message.text in self.mock_responses:
            response = self.mock_responses[message.text]
            self.responses.append(response)
            return response

        # Check for natural language patterns
        text_lower = message.text.lower()
        for pattern, response in self.mock_responses.items():
            if pattern.lower() in text_lower and not pattern.startswith("/"):
                self.responses.append(response)
                return response

        # Default response for unrecognized messages
        default_response = AgentResponse(
            message="🤔 I'm not sure how to help with that. Try /help for available commands.",
            success=False
        )
        self.responses.append(default_response)
        return default_response

    async def route_contact_share(self, message: TelegramMessage) -> AgentResponse:
        """Mock contact share routing."""
        logger.info(f"📱 MockAgenticMessageRouter: Processing contact share from {message.username}")

        response = AgentResponse(
            message="✅ Thank you for sharing your contact information! I've registered your phone number.",
            success=True
        )
        self.responses.append(response)
        return response

    def convert_telegram_update_to_message(self, update: MockUpdate, command_name: str = None) -> TelegramMessage:
        """Convert mock update to TelegramMessage."""
        return TelegramMessage(
            text=update.message.text,
            user_id=update.effective_user.id,
            username=update.effective_user.username or "unknown",
            chat_id=update.effective_chat.id,
            chat_type=self._determine_chat_type(update.effective_chat.id),
            team_id=self.team_id,
            raw_update=update
        )

    def _determine_chat_type(self, chat_id: str) -> ChatType:
        """Determine chat type based on chat ID."""
        # Mock logic - in real implementation this would check against configured chat IDs
        if chat_id.endswith("000"):  # Mock main chat pattern
            return ChatType.MAIN
        elif chat_id.endswith("111"):  # Mock leadership chat pattern
            return ChatType.LEADERSHIP
        else:
            return ChatType.MAIN  # Default to main chat

    def set_chat_ids(self, main_chat_id: str, leadership_chat_id: str):
        """Set chat IDs for routing."""
        self.main_chat_id = main_chat_id
        self.leadership_chat_id = leadership_chat_id
        logger.info(f"🔧 MockAgenticMessageRouter: Set chat IDs - Main: {main_chat_id}, Leadership: {leadership_chat_id}")


class MockTelegramBotService(TelegramBotServiceInterface):
    """
    Mock implementation of TelegramBotService for isolated testing.

    This mock provides all the functionality of the real TelegramBotService
    without requiring actual Telegram API calls, making it perfect for:
    - Unit testing
    - Integration testing
    - Development without Telegram API access
    - CI/CD pipeline testing
    """

    def __init__(
        self,
        token: str,
        team_id: str,
        main_chat_id: str = None,
        leadership_chat_id: str = None,
        crewai_system=None,
    ):
        self.token = token
        self.team_id = team_id
        self.main_chat_id = main_chat_id or "-1001234567890"
        self.leadership_chat_id = leadership_chat_id or "-1001234567891"
        self.crewai_system = crewai_system

        # Mock state
        self._running = False
        self._polling_task = None

        # Message tracking for testing
        self.sent_messages: list[dict[str, Any]] = []
        self.received_messages: list[dict[str, Any]] = []
        self.command_handlers: list[str] = []
        self.error_count = 0

        # Initialize mock agentic router
        self.agentic_router = MockAgenticMessageRouter(team_id=team_id, crewai_system=crewai_system)
        if main_chat_id and leadership_chat_id:
            self.agentic_router.set_chat_ids(main_chat_id, leadership_chat_id)

        # Mock application
        self.app = Mock()
        self.app.bot = MockBot()

        logger.info(f"✅ MockTelegramBotService initialized for team {team_id}")

    async def start_polling(self) -> None:
        """Mock polling start."""
        try:
            logger.info("🚀 Starting mock Telegram bot polling...")

            # Simulate initialization delay
            await asyncio.sleep(0.1)

            self._running = True
            logger.info("✅ Mock Telegram bot polling started")

            # Test bot connection
            me = await self.app.bot.get_me()
            logger.info(f"✅ Mock bot connected: @{me.username} (ID: {me.id})")

        except Exception as e:
            logger.error(f"❌ Error starting mock bot polling: {e}")
            raise

    async def stop(self) -> None:
        """Mock bot stop."""
        try:
            logger.info("🛑 Stopping mock Telegram bot...")
            if self._running:
                self._running = False
                if self._polling_task:
                    self._polling_task.cancel()
            logger.info("✅ Mock Telegram bot stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping mock bot: {e}")
            raise

    async def send_message(self, chat_id: int | str, text: str, **kwargs) -> Any:
        """Mock message sending."""
        try:
            logger.info(f"📤 Mock send_message to {chat_id}: {text}")

            # Track sent messages for testing
            self.sent_messages.append({
                'chat_id': str(chat_id),
                'text': text,
                'kwargs': kwargs,
                'timestamp': datetime.now()
            })

            # Simulate network delay
            await asyncio.sleep(0.05)

            return MockMessage(text, str(chat_id), "bot", "mock_bot")

        except Exception as e:
            logger.error(f"❌ Error sending mock message: {e}")
            self.error_count += 1
            raise

    async def send_contact_share_button(self, chat_id: int | str, text: str):
        """Mock contact share button sending."""
        try:
            logger.info(f"📱 Mock send_contact_share_button to {chat_id}: {text}")

            # Track sent messages for testing
            self.sent_messages.append({
                'chat_id': str(chat_id),
                'text': text,
                'type': 'contact_share_button',
                'timestamp': datetime.now()
            })

            # Simulate network delay
            await asyncio.sleep(0.05)

            return MockMessage(text, str(chat_id), "bot", "mock_bot")

        except Exception as e:
            logger.error(f"❌ Error sending mock contact share button: {e}")
            self.error_count += 1
            raise

    async def _handle_natural_language_message(self, update: MockUpdate, context: MockContext):
        """Mock natural language message handling."""
        try:
            logger.info(f"💬 Mock handling NL message: {update.message.text}")

            # Track received messages
            self.received_messages.append({
                'type': 'natural_language',
                'text': update.message.text,
                'user_id': update.effective_user.id,
                'chat_id': update.effective_chat.id,
                'timestamp': datetime.now()
            })

            # Convert to TelegramMessage and route through agentic system
            message = self.agentic_router.convert_telegram_update_to_message(update)
            response = await self.agentic_router.route_message(message)

            # Send response
            await self._send_response(update, response)

        except Exception as e:
            logger.error(f"❌ Error handling mock NL message: {e}")
            await self._send_error_response(update, f"Error processing message: {e!s}")

    async def _handle_registered_command(self, update: MockUpdate, context: MockContext, command_name: str):
        """Mock registered command handling."""
        try:
            logger.info(f"⚡ Mock handling command: {command_name}")

            # Track received messages
            self.received_messages.append({
                'type': 'command',
                'command': command_name,
                'text': update.message.text,
                'user_id': update.effective_user.id,
                'chat_id': update.effective_chat.id,
                'timestamp': datetime.now()
            })

            # Convert to TelegramMessage and route through agentic system
            message = self.agentic_router.convert_telegram_update_to_message(update, command_name)
            response = await self.agentic_router.route_message(message)

            # Send response
            await self._send_response(update, response)

        except Exception as e:
            logger.error(f"❌ Error handling mock command: {e}")
            await self._send_error_response(update, f"Error processing command: {e!s}")

    async def _send_response(self, update: MockUpdate, response: AgentResponse):
        """Mock response sending."""
        try:
            if response.success:
                await update.message.reply_text(response.message)
                logger.info(f"✅ Mock response sent: {response.message}")
            else:
                await update.message.reply_text(f"❌ {response.message}")
                logger.warning(f"⚠️ Mock error response sent: {response.message}")

        except Exception as e:
            logger.error(f"❌ Error sending mock response: {e}")
            self.error_count += 1

    async def _send_error_response(self, update: MockUpdate, error_message: str):
        """Mock error response sending."""
        try:
            await update.message.reply_text(f"❌ {error_message}")
            logger.error(f"❌ Mock error response: {error_message}")
            self.error_count += 1
        except Exception as e:
            logger.error(f"❌ Error sending mock error response: {e}")

    def _determine_chat_type(self, chat_id: str) -> ChatType:
        """Mock chat type determination."""
        if chat_id == self.main_chat_id:
            return ChatType.MAIN
        elif chat_id == self.leadership_chat_id:
            return ChatType.LEADERSHIP
        else:
            return ChatType.MAIN  # Default to main chat

    def _is_agent_formatted_message(self, text: str) -> bool:
        """Mock agent formatted message check."""
        return True  # In mock, all messages are considered properly formatted

    # Testing utility methods
    def get_sent_messages(self) -> list[dict[str, Any]]:
        """Get all sent messages for testing."""
        return self.sent_messages.copy()

    def get_received_messages(self) -> list[dict[str, Any]]:
        """Get all received messages for testing."""
        return self.received_messages.copy()

    def get_agentic_responses(self) -> list[AgentResponse]:
        """Get all agentic router responses for testing."""
        return self.agentic_router.responses.copy()

    def clear_message_history(self):
        """Clear message history for testing."""
        self.sent_messages.clear()
        self.received_messages.clear()
        self.agentic_router.responses.clear()
        self.agentic_router.routed_messages.clear()
        self.error_count = 0

    def is_running(self) -> bool:
        """Check if the mock bot is running."""
        return self._running

    def get_error_count(self) -> int:
        """Get the number of errors encountered."""
        return self.error_count

    async def simulate_message(self, text: str, chat_id: str, user_id: str, username: str = None):
        """Simulate receiving a message for testing."""
        update = MockUpdate(text, chat_id, user_id, username)
        context = MockContext()

        if text.startswith("/"):
            command = text.split()[0]
            await self._handle_registered_command(update, context, command)
        else:
            await self._handle_natural_language_message(update, context)

    async def simulate_contact_share(self, phone: str, chat_id: str, user_id: str, username: str = None):
        """Simulate contact sharing for testing."""
        update = MockUpdate(f"Contact shared: {phone}", chat_id, user_id, username)
        message = self.agentic_router.convert_telegram_update_to_message(update)
        response = await self.agentic_router.route_contact_share(message)

        # Send response
        await self._send_response(update, response)
