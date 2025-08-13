from typing import Set, Union
from loguru import logger
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from kickai.agents.agentic_message_router import AgenticMessageRouter
from kickai.core.enums import ChatType
from kickai.features.communication.domain.interfaces.telegram_bot_service_interface import (
    TelegramBotServiceInterface,
)


class TelegramBotService(TelegramBotServiceInterface):
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
        self.main_chat_id = main_chat_id
        self.leadership_chat_id = leadership_chat_id
        self.crewai_system = crewai_system

        if not self.token:
            raise ValueError("TelegramBotService: token must be provided explicitly (not from env)")

        # Initialize the agentic message router
        # Initialize the real AgenticMessageRouter with lazy loading
        self.agentic_router = AgenticMessageRouter(team_id=team_id, crewai_system=crewai_system)
        self.agentic_router.team_id = self.team_id  # Add team_id to router
        if main_chat_id and leadership_chat_id:
            self.agentic_router.set_chat_ids(main_chat_id, leadership_chat_id)

        self.app = Application.builder().token(self.token).build()
        self._running = False
        self._setup_handlers()

    def _setup_handlers(self):
        """Set up message handlers for the Telegram bot using command registry."""
        try:
            from kickai.core.command_registry_initializer import get_initialized_command_registry

            # Get the properly initialized command registry
            # Handle context isolation by ensuring registry is accessible
            try:
                registry = get_initialized_command_registry()
                all_commands = registry.list_all_commands()
                logger.info(f"✅ Command registry initialized with {len(all_commands)} commands")
            except RuntimeError as e:
                if "Command registry not initialized" in str(e):
                    logger.critical(
                        "💥 CRITICAL SYSTEM ERROR: Command registry not accessible in TelegramBotService - this is a major system failure"
                    )
                    logger.critical(
                        "🚨 The system cannot function without the command registry. This indicates a serious initialization failure."
                    )
                    logger.critical(
                        "🛑 Failing fast to prevent unsafe bot operation without command validation"
                    )
                    raise RuntimeError(
                        f"CRITICAL SYSTEM ERROR: Command registry not accessible in TelegramBotService. "
                        f"This is a major system failure that prevents safe bot operation. "
                        f"Original error: {e}"
                    )
                else:
                    raise

            # Set up command handlers from registry with chat-type awareness
            command_handlers = []

            # ALL commands use agentic routing - no dedicated handlers
            # This ensures single source of truth and consistent processing
            for cmd_metadata in all_commands:
                # Use the generic agentic handler for all commands
                def create_handler(cmd_name):
                    return lambda update, context: self._handle_registered_command(
                        update, context, cmd_name
                    )

                handler = create_handler(cmd_metadata.name)
                command_handlers.append(CommandHandler(cmd_metadata.name.lstrip("/"), handler))
                logger.info(f"✅ Registered agentic command handler: {cmd_metadata.name}")

            # Add message handler for natural language processing
            message_handler = MessageHandler(
                filters.TEXT & ~filters.COMMAND, self._handle_natural_language_message
            )

            # Add contact handler for phone number sharing
            contact_handler = MessageHandler(filters.CONTACT, self._handle_contact_share)

            # Add debug handler to log all updates
            debug_handler = MessageHandler(filters.ALL, self._debug_handler)

            # Add all handlers to the application
            self.app.add_handlers(
                command_handlers + [message_handler, contact_handler, debug_handler]
            )

            logger.info(
                f"✅ Set up {len(command_handlers)} agentic command handlers and 1 message handler"
            )

        except Exception as e:
            logger.critical(f"💥 CRITICAL SYSTEM ERROR: Failed to set up handlers: {e}")
            logger.critical("🚨 The bot cannot function without proper handler setup")
            logger.critical("🛑 Failing fast to prevent unsafe bot operation")
            raise RuntimeError(
                f"CRITICAL SYSTEM ERROR: Failed to set up bot handlers. "
                f"This is a major system failure that prevents safe bot operation. "
                f"Original error: {e}"
            )

    def _setup_fallback_handlers(self):
        """Set up fallback handlers when command registry fails."""
        try:
            # All messages now use agentic routing - minimal fallback
            handlers = [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, self._handle_natural_language_message
                ),
                MessageHandler(filters.CONTACT, self._handle_contact_share),
            ]

            self.app.add_handlers(handlers)
            logger.info(f"✅ Set up {len(handlers)} fallback handlers")

        except Exception as e:
            logger.error(f"❌ Error setting up fallback handlers: {e}")

    async def _handle_natural_language_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle natural language messages through agentic system ONLY."""
        try:
            # Convert to domain message
            message = self.agentic_router.convert_telegram_update_to_message(update)

            # Route through agentic system (NO direct processing)
            response = await self.agentic_router.route_message(message)

            # Send response
            await self._send_response(update, response)

        except Exception as e:
            logger.error(f"Error in agentic message handling: {e}")
            await self._send_error_response(
                update, "I encountered an error processing your message."
            )

    async def _handle_contact_share(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle contact sharing for phone number linking."""
        try:
            logger.info(f"📱 Contact shared by user {update.effective_user.id}")

            # Extract contact information
            contact = update.message.contact
            phone_number = contact.phone_number
            user_id = contact.user_id if contact.user_id else update.effective_user.id
            username = update.effective_user.username

            # Validate that the contact belongs to the user
            if str(user_id) != str(update.effective_user.id):
                await self._send_error_response(
                    update, "❌ Please share your own contact information."
                )
                return

            # Convert to domain message with special handling for contact sharing
            message = self.agentic_router.convert_telegram_update_to_message(update)

            # Add contact information to the message
            message.contact_phone = phone_number
            message.contact_user_id = str(user_id)

            # Route through agentic system
            response = await self.agentic_router.route_contact_share(message)

            # Send response
            await self._send_response(update, response)

        except Exception as e:
            logger.error(f"Error in contact share handling: {e}")
            await self._send_error_response(
                update, "I encountered an error processing your contact information."
            )

    def _determine_chat_type(self, chat_id: str) -> ChatType:
        """Determine the chat type based on chat ID."""
        if chat_id == self.main_chat_id:
            return ChatType.MAIN
        elif chat_id == self.leadership_chat_id:
            return ChatType.LEADERSHIP
        else:
            return ChatType.PRIVATE

    async def _handle_registered_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, command_name: str
    ):
        """Handle registered commands through agentic system ONLY."""
        try:
            # Convert to domain message
            message = self.agentic_router.convert_telegram_update_to_message(update, command_name)

            # Route through agentic system (NO direct processing)
            response = await self.agentic_router.route_message(message)

            # Send response
            await self._send_response(update, response)

        except Exception as e:
            logger.error(f"Error in agentic command handling: {e}")
            await self._send_error_response(
                update, "I encountered an error processing your command."
            )

    async def _send_response(self, update: Update, response):
        """Send response to user."""
        try:
            if hasattr(response, "message"):
                # AgentResponse object
                message_text = response.message
                success = response.success
            else:
                # String response
                message_text = str(response)
                success = True

            if not success:
                await self._send_error_response(update, message_text)
                return

            # Format JSON responses for human readability
            from kickai.features.communication.domain.services.response_formatter import ResponseFormatter
            formatter = ResponseFormatter()
            formatted_text = formatter.format_for_telegram(message_text)
            
            logger.debug(f"🔍 Original message: {message_text[:100]}...")
            logger.debug(f"🔍 Formatted message: {formatted_text[:100]}...")

            # Check if we need to send contact sharing button
            if hasattr(response, "needs_contact_button") and response.needs_contact_button:
                logger.info("📱 Sending message with contact sharing button")
                await self.send_contact_share_button(update.effective_chat.id, formatted_text)
            else:
                # Send as plain text - no Markdown or HTML formatting
                logger.debug("✅ Sending formatted message as plain text")
                await update.message.reply_text(formatted_text)

            logger.info("✅ Agentic response sent successfully")

        except Exception as e:
            logger.error(f"❌ Error sending response: {e}")
            await self._send_error_response(update, "I encountered an error sending the response.")

    async def _send_error_response(self, update: Update, error_message: str):
        """Send an error response to the user."""
        try:
            await update.message.reply_text(f"❌ {error_message}")
        except Exception as e:
            logger.error(f"❌ Error sending error response: {e}")

    async def start_polling(self) -> None:
        """Start the bot polling."""
        try:
            logger.info("Starting Telegram bot polling...")
            await self.app.initialize()
            await self.app.start()

            # Add debug logging for polling setup
            logger.info(f"🔍 Bot token: {self.token[:10]}...")
            logger.info(f"🔍 Main chat ID: {self.main_chat_id}")
            logger.info(f"🔍 Leadership chat ID: {self.leadership_chat_id}")

            # Start polling with basic parameters
            await self.app.updater.start_polling(
                poll_interval=1.0,  # Poll every second
                timeout=30,  # 30 second timeout
                bootstrap_retries=5,  # Retry 5 times on startup
            )
            self._running = True
            logger.info("Telegram bot polling started.")

            # Test bot connection
            try:
                me = await self.app.bot.get_me()
                logger.info(f"✅ Bot connected successfully: @{me.username} (ID: {me.id})")
            except Exception as e:
                logger.error(f"❌ Bot connection test failed: {e}")

        except Exception as e:
            logger.error(f"❌ Error starting bot polling: {e}")
            raise

    async def _debug_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Debug handler to log all incoming updates."""
        try:
            # Get the update type instead of message type
            update_type = type(update).__name__
            logger.info(f"🔍 DEBUG: Received update - Type: {update_type}")

            if update.effective_message:
                message_type = type(update.effective_message).__name__
                logger.info(f"🔍 DEBUG: Message Type: {message_type}")
                logger.info(
                    f"🔍 DEBUG: Chat ID: {update.effective_chat.id}, User ID: {update.effective_user.id if update.effective_user else 'None'}"
                )
                if update.effective_message.text:
                    logger.info(f"🔍 DEBUG: Text: {update.effective_message.text[:100]}...")
        except Exception as e:
            logger.error(f"❌ Error in debug handler: {e}")

    async def send_message(self, chat_id: Union[int, str], text: str, **kwargs):
        """Send a message to a specific chat in plain text."""
        try:
            # Sanitize text to ensure plain text output
            sanitized_text = self._sanitize_for_plain_text(text)
            logger.info(f"Sending plain text message to chat_id={chat_id}: {sanitized_text}")
            
            # Explicitly send as plain text (no parse_mode)
            await self.app.bot.send_message(
                chat_id=chat_id, 
                text=sanitized_text, 
                parse_mode=None,  # Explicitly set to None for plain text
                **kwargs
            )
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            raise

    def _sanitize_for_plain_text(self, text: str) -> str:
        """Remove any formatting characters to ensure plain text output."""
        if not text:
            return text
            
        # Remove common markdown characters that might cause issues
        text = text.replace('*', '').replace('_', '').replace('`', '')
        text = text.replace('**', '').replace('__', '').replace('~~', '')
        text = text.replace('#', '').replace('##', '').replace('###', '')
        
        # Remove HTML-like tags
        import re
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove HTML entities
        text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    async def send_contact_share_button(self, chat_id: Union[int, str], text: str):
        """Send a message with a contact sharing button."""
        try:
            keyboard = [[KeyboardButton(text="📱 Share My Phone Number", request_contact=True)]]
            reply_markup = ReplyKeyboardMarkup(
                keyboard, one_time_keyboard=True, resize_keyboard=True
            )

            await self.app.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error sending contact share button: {e}")
            # Fallback to regular message
            await self.send_message(chat_id, text)

    def _is_agent_formatted_message(self, text: str) -> bool:
        """Check if message is already properly formatted by an agent."""
        # With plain text, all messages are treated the same
        return True

    async def stop(self) -> None:
        """Stop the bot."""
        try:
            logger.info("Stopping Telegram bot...")
            if self._running:
                await self.app.updater.stop()
                await self.app.stop()
                await self.app.shutdown()
                self._running = False
            logger.info("Telegram bot stopped.")
        except Exception as e:
            logger.error(f"❌ Error stopping bot: {e}")
            raise
