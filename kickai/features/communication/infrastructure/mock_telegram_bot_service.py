#!/usr/bin/env python3
"""
Mock Telegram Bot Service

This module provides a mock implementation of TelegramBotService that can work in two modes:
1. UI Integration Mode: Sends messages to Mock Telegram UI (http://localhost:8001)
2. Testing Mode: Isolated testing without external dependencies

The mode is determined by the USE_MOCK_UI environment variable.
"""

import asyncio
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from unittest.mock import Mock

import aiohttp
from loguru import logger

from kickai.core.enums import ChatType

# Import centralized types
from kickai.core.types import AgentResponse, TelegramMessage
from kickai.features.communication.domain.interfaces.telegram_bot_service_interface import (
    TelegramBotServiceInterface,
)


@dataclass
class MockUpdate:
    """Mock Telegram Update object for testing."""

    message: "MockMessage"
    effective_message: "MockMessage"
    effective_chat: "MockChat"
    effective_user: "MockUser"

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
    name: str = "Mock User"
    first_name: str = "Mock"  # Keep for Telegram API compatibility
    last_name: str = "User"  # Keep for Telegram API compatibility


@dataclass
class MockContext:
    """Mock Telegram Context object for testing."""

    bot: "MockBot"

    def __init__(self):
        self.bot = MockBot()


class MockBot:
    """Mock Telegram Bot object for testing."""

    def __init__(self):
        self.username = "mock_bot"
        self.id = "123456789"
        self.name = "Mock Bot"
        self.first_name = "Mock"  # Keep for Telegram API compatibility
        self.last_name = "Bot"  # Keep for Telegram API compatibility

    async def get_me(self):
        """Mock get_me method."""
        return self

    async def send_message(self, chat_id: int | str, text: str, **kwargs):
        """Mock send_message method."""
        logger.info(f"📤 Mock bot send_message: {text}")
        return MockMessage(text, str(chat_id), "bot", "mock_bot")


# MockTelegramMessageAdapter removed - use real TelegramMessageAdapter instead


class MockTelegramBotService(TelegramBotServiceInterface):
    """
    Mock implementation of TelegramBotService with dual mode support.

    Modes:
    1. UI Integration Mode (USE_MOCK_UI=true): Sends messages to Mock Telegram UI
    2. Testing Mode (USE_MOCK_UI=false): Isolated testing without external dependencies

    This provides all the functionality of the real TelegramBotService for:
    - Development with Mock Telegram UI integration
    - Unit testing
    - Integration testing
    - CI/CD pipeline testing
    """

    def __init__(
        self,
        token: str,
        team_id: str,
        main_chat_id: str,
        leadership_chat_id: str,
        crewai_system=None,
    ):
        self.token = token
        self.team_id = team_id
        self.main_chat_id = main_chat_id
        self.leadership_chat_id = leadership_chat_id
        self.crewai_system = crewai_system

        # Validate all required parameters
        if not self.token:
            raise ValueError("MockTelegramBotService: token must be provided")

        if not self.team_id:
            raise ValueError("MockTelegramBotService: team_id must be provided")

        if not self.main_chat_id:
            raise ValueError("MockTelegramBotService: main_chat_id must be provided")

        if not self.leadership_chat_id:
            raise ValueError("MockTelegramBotService: leadership_chat_id must be provided")

        # Validate parameter types
        if not isinstance(self.token, str):
            raise TypeError("MockTelegramBotService: token must be a string")

        if not isinstance(self.team_id, str):
            raise TypeError("MockTelegramBotService: team_id must be a string")

        if not isinstance(self.main_chat_id, str):
            raise TypeError("MockTelegramBotService: main_chat_id must be a string")

        if not isinstance(self.leadership_chat_id, str):
            raise TypeError("MockTelegramBotService: leadership_chat_id must be a string")

        # Validate chat IDs are different
        if self.main_chat_id == self.leadership_chat_id:
            raise ValueError(
                "MockTelegramBotService: main_chat_id and leadership_chat_id must be different"
            )

        # Determine operation mode - auto-detect Mock UI or use environment override
        self.use_mock_ui = self._should_use_mock_ui()
        self.mock_api_base_url = os.getenv("MOCK_API_BASE_URL", "http://localhost:8001/api")
        self.mock_ui_detected = False

        # Bot user for sending messages to UI
        self.bot_user_id = 9999  # Special bot user ID
        self.bot_username = "kickai_bot"
        self.bot_name = "KICKAI Bot"

        # Mock state
        self._running = False
        self._polling_task = None

        # Message tracking for testing
        self.sent_messages: list[dict[str, Any]] = []
        self.received_messages: list[dict[str, Any]] = []
        self.command_handlers: list[str] = []
        self.error_count = 0

        # Initialize real agentic router
        from kickai.agents.telegram_message_adapter import TelegramMessageAdapter

        self.message_adapter = TelegramMessageAdapter(team_id=team_id)

        # Set chat IDs for proper chat type determination
        self.message_adapter.set_chat_ids(main_chat_id, leadership_chat_id)

        # Mock application
        self.app = Mock()
        self.app.bot = MockBot()

        mode_name = "UI Integration" if self.use_mock_ui else "Testing"
        logger.info(f"✅ MockTelegramBotService initialized for team {team_id} in {mode_name} mode")
        if self.use_mock_ui:
            logger.info(f"📱 Mock UI URL: {self.mock_api_base_url}")
            logger.info(
                f"💬 Main chat: {self.main_chat_id}, Leadership chat: {self.leadership_chat_id}"
            )
            logger.info(
                f"🔍 Auto-detection mode: {'enabled' if not os.getenv('USE_MOCK_UI') else 'disabled (override set)'}"
            )

    async def start_polling(self) -> None:
        """Mock polling start with optional UI integration test."""
        try:
            mode_desc = "UI Integration" if self.use_mock_ui else "Testing"
            logger.info(f"🚀 Starting mock Telegram bot polling in {mode_desc} mode...")

            # Test Mock UI connection if in UI mode
            if self.use_mock_ui:
                try:
                    await self._test_mock_ui_connection()
                    self.mock_ui_detected = True
                    logger.info("✅ Mock UI connection verified - messages will be sent to UI")
                except Exception as e:
                    logger.warning(f"⚠️ Mock UI connection failed: {e}")
                    if os.getenv("USE_MOCK_UI", "").lower() == "true":
                        # If explicitly set, fail startup
                        raise
                    else:
                        # If auto-detected, fall back to testing mode
                        logger.info("🔄 Falling back to testing mode (no Mock UI available)")
                        self.use_mock_ui = False
                        self.mock_ui_detected = False

            # Simulate initialization delay
            await asyncio.sleep(0.1)

            self._running = True
            logger.info(f"✅ Mock Telegram bot polling started in {mode_desc} mode")

            # Test bot connection
            me = await self.app.bot.get_me()
            logger.info(f"✅ Mock bot connected: @{me.username} (ID: {me.id})")

            if self.use_mock_ui:
                logger.info("📱 Messages will be sent to Mock Telegram UI at http://localhost:8001")

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
        """Mock message sending with optional UI integration."""
        try:
            chat_id_str = str(chat_id)
            chat_context = self._get_chat_context(chat_id_str)

            logger.info(f"📤 Mock send_message to {chat_context} chat ({chat_id}): {text[:50]}...")

            # Track sent messages for testing
            message_record = {
                "chat_id": chat_id_str,
                "text": text,
                "type": "message",
                "chat_context": chat_context,
                "kwargs": kwargs,
                "timestamp": datetime.now(),
            }
            self.sent_messages.append(message_record)

            # Send to Mock UI if in UI mode and detected
            if self.use_mock_ui and self.mock_ui_detected:
                try:
                    await self._send_to_mock_ui(chat_id_str, text)
                except Exception as ui_error:
                    logger.warning(f"⚠️ Failed to send to Mock UI: {ui_error}")
                    # Try to re-detect Mock UI for next time
                    self.mock_ui_detected = False
                    # Don't fail the message sending - just log it
                    await asyncio.sleep(0.05)  # Simulate delay
            else:
                # Simulate network delay for testing mode
                await asyncio.sleep(0.05)

            logger.info(f"✅ Message sent successfully to {chat_context} chat")
            return MockMessage(text, chat_id_str, "bot", "mock_bot")

        except Exception as e:
            logger.error(f"❌ Error sending mock message: {e}")
            self.error_count += 1
            raise

    async def send_contact_share_button(self, chat_id: int | str, text: str):
        """Mock contact share button sending with UI integration."""
        try:
            chat_id_str = str(chat_id)
            chat_context = self._get_chat_context(chat_id_str)

            logger.info(
                f"📱 Mock send_contact_share_button to {chat_context} chat ({chat_id}): {text}"
            )

            # Track sent messages for testing
            message_record = {
                "chat_id": chat_id_str,
                "text": text,
                "type": "contact_share_button",
                "chat_context": chat_context,
                "timestamp": datetime.now(),
            }
            self.sent_messages.append(message_record)

            # Send to Mock UI if available (using "text" type as Mock UI doesn't support "contact_share")
            if self.use_mock_ui and self.mock_ui_detected:
                try:
                    await self._send_to_mock_ui(chat_id_str, f"🔗 {text}", "text")
                except Exception as ui_error:
                    logger.warning(f"⚠️ Failed to send contact button to Mock UI: {ui_error}")
                    self.mock_ui_detected = False
            else:
                # Simulate network delay for testing mode
                await asyncio.sleep(0.05)

            return MockMessage(text, chat_id_str, "bot", "mock_bot")

        except Exception as e:
            logger.error(f"❌ Error sending mock contact share button: {e}")
            self.error_count += 1
            raise

    async def _handle_natural_language_message(self, update: MockUpdate, context: MockContext):
        """Mock natural language message handling."""
        try:
            logger.info(f"💬 Mock handling NL message: {update.message.text}")

            # Track received messages
            self.received_messages.append(
                {
                    "type": "natural_language",
                    "text": update.message.text,
                    "user_id": update.effective_user.id,
                    "chat_id": update.effective_chat.id,
                    "timestamp": datetime.now(),
                }
            )

            # Convert to TelegramMessage and route through agentic system
            message = self._convert_telegram_update_to_message(update)
            response = await self.message_adapter.process_message(message)

            # Send response
            await self._send_response(update, response)

        except Exception as e:
            logger.error(f"❌ Error handling mock NL message: {e}")
            await self._send_error_response(update, f"Error processing message: {e!s}")

    async def _handle_registered_command(
        self, update: MockUpdate, context: MockContext, command_name: str
    ):
        """Mock registered command handling."""
        try:
            logger.info(f"⚡ Mock handling command: {command_name}")

            # Track received messages
            self.received_messages.append(
                {
                    "type": "command",
                    "command": command_name,
                    "text": update.message.text,
                    "user_id": update.effective_user.id,
                    "chat_id": update.effective_chat.id,
                    "timestamp": datetime.now(),
                }
            )

            # Convert to TelegramMessage and route through agentic system
            message = self._convert_telegram_update_to_message(update, command_name)
            response = await self.message_adapter.process_message(message)

            # Send response
            await self._send_response(update, response)

        except Exception as e:
            logger.error(f"❌ Error handling mock command: {e}")
            await self._send_error_response(update, f"Error processing command: {e!s}")

    async def _send_response(self, update: MockUpdate, response: AgentResponse):
        """Mock response sending."""
        try:
            message_text = response.message

            if response.success:
                # Parse JSON response to extract the actual message content
                try:
                    import json

                    parsed_response = json.loads(message_text)
                    if isinstance(parsed_response, dict):
                        if "data" in parsed_response:
                            formatted_text = parsed_response["data"]
                        elif "message" in parsed_response:
                            formatted_text = parsed_response["message"]
                        else:
                            formatted_text = message_text
                    else:
                        formatted_text = message_text
                except (json.JSONDecodeError, TypeError):
                    # If not JSON, use the message text directly
                    formatted_text = message_text

                await update.message.reply_text(formatted_text)
                logger.info(f"✅ Mock response sent: {formatted_text[:100]}...")
            else:
                await update.message.reply_text(f"❌ {message_text}")
                logger.warning(f"⚠️ Mock error response sent: {message_text}")

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

    def _convert_telegram_update_to_message(
        self, update: MockUpdate, command_name: str = None
    ) -> TelegramMessage:
        """Convert mock update to TelegramMessage."""
        return TelegramMessage(
            text=update.message.text,
            telegram_id=update.effective_user.id,
            username=update.effective_user.username or "unknown",
            chat_id=update.effective_chat.id,
            chat_type=self._determine_chat_type(update.effective_chat.id),
            team_id=self.team_id,
            raw_update=update,
        )

    def _determine_chat_type(self, chat_id: str) -> ChatType:
        """Mock chat type determination."""
        if chat_id == self.main_chat_id:
            return ChatType.MAIN
        elif chat_id == self.leadership_chat_id:
            return ChatType.LEADERSHIP
        else:
            return ChatType.MAIN  # Default to main chat

    # Testing utility methods
    def get_sent_messages(self) -> list[dict[str, Any]]:
        """Get all sent messages for testing."""
        return self.sent_messages.copy()

    def get_received_messages(self) -> list[dict[str, Any]]:
        """Get all received messages for testing."""
        return self.received_messages.copy()

    def get_agentic_responses(self) -> list[AgentResponse]:
        """Get all agentic router responses for testing."""
        # Real TelegramMessageAdapter doesn't store responses, so return empty list
        return []

    def clear_message_history(self):
        """Clear message history for testing."""
        self.sent_messages.clear()
        self.received_messages.clear()
        # Real TelegramMessageAdapter doesn't store responses/routed_messages
        self.error_count = 0

    def is_running(self) -> bool:
        """Check if the mock bot is running."""
        return self._running

    def get_error_count(self) -> int:
        """Get the number of errors encountered."""
        return self.error_count

    def get_mock_ui_status(self) -> dict[str, Any]:
        """Get the status of Mock UI integration."""
        return {
            "use_mock_ui": self.use_mock_ui,
            "mock_ui_detected": self.mock_ui_detected,
            "mock_api_base_url": self.mock_api_base_url,
            "main_chat_id": self.main_chat_id,
            "leadership_chat_id": self.leadership_chat_id,
            "bot_user_id": self.bot_user_id,
            "auto_detection_enabled": os.getenv("USE_MOCK_UI") is None,
        }

    async def test_mock_ui_connectivity(self) -> dict[str, Any]:
        """Test Mock UI connectivity and return status."""
        if not self.use_mock_ui:
            return {"available": False, "reason": "Mock UI mode disabled", "status": "disabled"}

        try:
            await self._test_mock_ui_connection()
            self.mock_ui_detected = True
            return {"available": True, "status": "connected", "url": self.mock_api_base_url}
        except Exception as e:
            self.mock_ui_detected = False
            return {
                "available": False,
                "reason": str(e),
                "status": "error",
                "url": self.mock_api_base_url,
            }

    async def simulate_message(self, text: str, chat_id: str, user_id: str, username: str = None):
        """Simulate receiving a message for testing."""
        update = MockUpdate(text, chat_id, user_id, username)
        context = MockContext()

        if text.startswith("/"):
            command = text.split()[0]
            await self._handle_registered_command(update, context, command)
        else:
            await self._handle_natural_language_message(update, context)

    async def simulate_contact_share(
        self, phone: str, chat_id: str, user_id: str, username: str = None
    ):
        """Simulate contact sharing for testing."""
        update = MockUpdate(f"Contact shared: {phone}", chat_id, user_id, username)
        message = self._convert_telegram_update_to_message(update)
        # Add contact phone to message for routing
        message.contact_phone = phone
        response = await self.message_adapter.process_contact_share(message)

        # Send response
        await self._send_response(update, response)

    # UI Integration Helper Methods

    async def _test_mock_ui_connection(self) -> None:
        """Test connection to the Mock Telegram UI and ensure bot user exists."""
        try:
            test_url = f"{self.mock_api_base_url}/stats"

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(test_url) as response:
                    if response.status == 200:
                        stats = await response.json()
                        logger.info("✅ Mock UI connection test successful")
                        logger.info(
                            f"📊 Mock UI stats: {stats.get('total_users', 0)} users, "
                            f"{stats.get('total_messages', 0)} messages"
                        )

                        # Ensure bot user exists in mock UI
                        await self._ensure_bot_user_exists()

                    else:
                        raise Exception(f"Mock UI returned status {response.status}")

        except TimeoutError:
            raise Exception("Mock UI connection timeout - is it running at http://localhost:8001?")
        except aiohttp.ClientConnectionError:
            raise Exception("Cannot connect to Mock UI - is it running at http://localhost:8001?")
        except Exception as e:
            raise Exception(f"Mock UI test failed: {e}")

    async def _ensure_bot_user_exists(self) -> None:
        """Ensure the bot user exists in the Mock UI."""
        try:
            # Check if bot user already exists
            users_url = f"{self.mock_api_base_url}/users"

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(users_url) as response:
                    if response.status == 200:
                        users = await response.json()

                        # Check if bot user exists by username
                        bot_user = None
                        for user in users:
                            if user.get("username") == self.bot_username:
                                bot_user = user
                                break

                        if bot_user:
                            # Update bot_user_id to the actual ID
                            self.bot_user_id = bot_user.get("id", self.bot_user_id)
                            logger.info(
                                f"✅ Bot user {self.bot_username} already exists with ID {self.bot_user_id}"
                            )
                        else:
                            # Create bot user
                            logger.info(f"🤖 Creating bot user {self.bot_username}")
                            await self._create_bot_user()
                    else:
                        logger.warning(f"⚠️ Could not check users: status {response.status}")

        except Exception as e:
            logger.warning(f"⚠️ Could not ensure bot user exists: {e}")
            # Don't fail initialization for this - the API might handle it differently

    async def _create_bot_user(self) -> None:
        """Create the bot user in the Mock UI."""
        try:
            create_user_url = f"{self.mock_api_base_url}/users"

            # Bot user data
            bot_user_data = {
                "username": self.bot_username,
                "first_name": self.bot_name,
                "last_name": None,
                "role": "admin",
                "phone_number": None,
            }

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.post(create_user_url, json=bot_user_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Update bot_user_id to the actual created ID
                        actual_id = result.get("id")
                        if actual_id:
                            self.bot_user_id = actual_id
                            logger.info(
                                f"✅ Bot user created successfully with ID {actual_id}: {result}"
                            )
                        else:
                            logger.info(f"✅ Bot user created successfully: {result}")
                    else:
                        error_text = await response.text()
                        logger.warning(
                            f"⚠️ Could not create bot user: {response.status} - {error_text}"
                        )

        except Exception as e:
            logger.warning(f"⚠️ Error creating bot user: {e}")
            # Don't fail - the bot might work without explicit user creation

    async def send_announcement(self, chat_id: int | str, message: str, **kwargs) -> Any:
        """Send an announcement message with UI integration."""
        try:
            chat_id_str = str(chat_id)
            chat_context = self._get_chat_context(chat_id_str)
            announcement_text = f"📢 ANNOUNCEMENT: {message}"

            logger.info(
                f"📢 Mock send_announcement to {chat_context} chat ({chat_id}): {message[:50]}..."
            )

            # Track sent messages
            message_record = {
                "chat_id": chat_id_str,
                "text": announcement_text,
                "type": "announcement",
                "chat_context": chat_context,
                "kwargs": kwargs,
                "timestamp": datetime.now(),
            }
            self.sent_messages.append(message_record)

            # Send to Mock UI if available (using "text" type as Mock UI doesn't support "announcement")
            if self.use_mock_ui and self.mock_ui_detected:
                try:
                    await self._send_to_mock_ui(chat_id_str, announcement_text, "text")
                except Exception as ui_error:
                    logger.warning(f"⚠️ Failed to send announcement to Mock UI: {ui_error}")
                    self.mock_ui_detected = False
            else:
                await asyncio.sleep(0.05)

            logger.info(f"✅ Announcement sent successfully to {chat_context} chat")
            return MockMessage(announcement_text, chat_id_str, "bot", "mock_bot")

        except Exception as e:
            logger.error(f"❌ Error sending mock announcement: {e}")
            self.error_count += 1
            raise

    async def send_poll(
        self, chat_id: int | str, question: str, options: list[str], **kwargs
    ) -> Any:
        """Send a poll with UI integration."""
        try:
            chat_id_str = str(chat_id)
            chat_context = self._get_chat_context(chat_id_str)
            poll_text = f"🗳️ POLL: {question}\n" + "\n".join(
                [f"{i+1}. {opt}" for i, opt in enumerate(options)]
            )

            logger.info(f"🗳️ Mock send_poll to {chat_context} chat ({chat_id}): {question}")

            # Track sent messages
            message_record = {
                "chat_id": chat_id_str,
                "text": poll_text,
                "type": "poll",
                "chat_context": chat_context,
                "question": question,
                "options": options,
                "kwargs": kwargs,
                "timestamp": datetime.now(),
            }
            self.sent_messages.append(message_record)

            # Send to Mock UI if available (using "text" type as Mock UI doesn't support "poll")
            if self.use_mock_ui and self.mock_ui_detected:
                try:
                    await self._send_to_mock_ui(chat_id_str, poll_text, "text")
                except Exception as ui_error:
                    logger.warning(f"⚠️ Failed to send poll to Mock UI: {ui_error}")
                    self.mock_ui_detected = False
            else:
                await asyncio.sleep(0.05)

            logger.info(f"✅ Poll sent successfully to {chat_context} chat")
            return MockMessage(poll_text, chat_id_str, "bot", "mock_bot")

        except Exception as e:
            logger.error(f"❌ Error sending mock poll: {e}")
            self.error_count += 1
            raise

    async def send_team_announcement(
        self, message: str, target_chat: str = "main", **kwargs
    ) -> Any:
        """Send a team announcement to specified chat with UI integration."""
        try:
            # Determine target chat ID based on target_chat parameter
            if target_chat.lower() == "leadership":
                chat_id = self.leadership_chat_id
            else:
                chat_id = self.main_chat_id

            return await self.send_announcement(chat_id, message, **kwargs)

        except Exception as e:
            logger.error(f"❌ Error sending team announcement: {e}")
            self.error_count += 1
            raise

    async def broadcast_message(
        self, message: str, include_leadership: bool = True, **kwargs
    ) -> list[Any]:
        """Broadcast a message to multiple chats with UI integration."""
        try:
            results = []

            # Send to main chat
            main_result = await self.send_message(self.main_chat_id, message, **kwargs)
            results.append(main_result)

            # Send to leadership chat if requested
            if include_leadership:
                leadership_result = await self.send_message(
                    self.leadership_chat_id, message, **kwargs
                )
                results.append(leadership_result)

            logger.info(f"✅ Broadcast message sent to {len(results)} chats")
            return results

        except Exception as e:
            logger.error(f"❌ Error broadcasting message: {e}")
            self.error_count += 1
            raise

    async def _send_to_mock_ui(self, chat_id: str, text: str, message_type: str = "text") -> dict:
        """Send a message to the Mock Telegram UI with enhanced error handling."""
        try:
            # Prepare message data for mock API
            message_data = {
                "user_id": self.bot_user_id,
                "chat_id": int(chat_id),
                "text": text,
                "message_type": message_type,
            }

            url = f"{self.mock_api_base_url}/send_message"

            # Use a shorter timeout for Mock UI to avoid blocking
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.post(url, json=message_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.debug(f"📡 Mock UI message sent successfully: {text[:50]}...")
                        return result
                    else:
                        error_text = await response.text()
                        raise Exception(f"Mock UI API error {response.status}: {error_text}")

        except TimeoutError:
            # Mark Mock UI as unavailable but don't fail the operation
            self.mock_ui_detected = False
            raise Exception("Mock UI timeout - marking as unavailable")
        except aiohttp.ClientConnectionError:
            # Mark Mock UI as unavailable but don't fail the operation
            self.mock_ui_detected = False
            raise Exception("Mock UI connection error - marking as unavailable")
        except Exception as e:
            logger.error(f"❌ Failed to send message to Mock UI: {e}")
            raise

    def _should_use_mock_ui(self) -> bool:
        """Determine if Mock UI should be used based on environment and detection."""
        # Check for explicit environment override first
        explicit_setting = os.getenv("USE_MOCK_UI")
        if explicit_setting is not None:
            return explicit_setting.lower() == "true"

        # Auto-detect: Check if we're in development mode and Mock UI might be available
        env_mode = os.getenv("ENVIRONMENT", "development").lower()
        ai_provider = os.getenv("AI_PROVIDER", "groq").lower()

        # Use Mock UI in development with groq/local providers
        if env_mode == "development" and ai_provider in ["groq", "ollama", "local"]:
            return True

        # Use Mock UI if running local bot (check for local bot indicator)
        if os.getenv("KICKAI_LOCAL_MODE", "false").lower() == "true":
            return True

        return False

    def _get_chat_context(self, chat_id: str) -> str:
        """Get chat context from chat ID."""
        if chat_id == self.main_chat_id:
            return "main"
        elif chat_id == self.leadership_chat_id:
            return "leadership"
        else:
            return "main"  # Default to main
