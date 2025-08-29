# Standard library imports
from datetime import datetime
from typing import Set, Union

# Third-party imports
from loguru import logger
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Local imports
from kickai.agents.agentic_message_router import AgenticMessageRouter
from kickai.core.enums import ChatType
from kickai.features.communication.domain.interfaces.telegram_bot_service_interface import (
    TelegramBotServiceInterface,
)

# Constants
POLL_INTERVAL = 1.0
POLL_TIMEOUT = 30
BOOTSTRAP_RETRIES = 5
TOKEN_DISPLAY_LENGTH = 10
MESSAGE_PREVIEW_LENGTH = 100


class TelegramBotService(TelegramBotServiceInterface):
    """
    Real Telegram bot service implementation for production use.
    
    This service handles all Telegram bot interactions through the agentic system.
    All user messages are routed through CrewAI agents for processing, ensuring
    consistent behavior and proper access control.
    
    Attributes:
        token: Telegram bot token for API authentication
        team_id: Team identifier for multi-team support
        main_chat_id: Chat ID for the main team chat
        leadership_chat_id: Chat ID for the leadership chat
        crewai_system: CrewAI system for agent orchestration
        agentic_router: Router for message processing
        app: Telegram application instance
        _running: Bot running state
        
    Raises:
        ValueError: When required parameters are missing or invalid
        TypeError: When parameters have incorrect types
        RuntimeError: When system initialization fails
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
            raise ValueError("TelegramBotService: token must be provided explicitly (not from env)")
        
        if not self.team_id:
            raise ValueError("TelegramBotService: team_id must be provided")
        
        if not self.main_chat_id:
            raise ValueError("TelegramBotService: main_chat_id must be provided")
        
        if not self.leadership_chat_id:
            raise ValueError("TelegramBotService: leadership_chat_id must be provided")
        
        # Validate parameter types
        if not isinstance(self.token, str):
            raise TypeError("TelegramBotService: token must be a string")
        
        if not isinstance(self.team_id, str):
            raise TypeError("TelegramBotService: team_id must be a string")
        
        if not isinstance(self.main_chat_id, str):
            raise TypeError("TelegramBotService: main_chat_id must be a string")
        
        if not isinstance(self.leadership_chat_id, str):
            raise TypeError("TelegramBotService: leadership_chat_id must be a string")
        
        # Validate chat IDs are different
        if self.main_chat_id == self.leadership_chat_id:
            raise ValueError("TelegramBotService: main_chat_id and leadership_chat_id must be different")

        # Initialize the agentic message router
        # Initialize the real AgenticMessageRouter with lazy loading
        self.agentic_router = AgenticMessageRouter(team_id=team_id, crewai_system=crewai_system)
        
        # Set chat IDs for proper chat type determination
        self.agentic_router.set_chat_ids(main_chat_id, leadership_chat_id)

        self.app = Application.builder().token(self.token).build()
        self._running = False
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """
        Set up message handlers for the Telegram bot using command registry.
        
        Configures command handlers, message handlers, and contact handlers
        for the bot application. All handlers route through the agentic system.
        
        Raises:
            RuntimeError: When command registry is not accessible or handler setup fails
        """
        try:
            # Get command registry
            registry = self._get_command_registry()
            
            # Set up handlers
            command_handlers = self._create_command_handlers(registry)
            message_handlers = self._create_message_handlers()
            
            # Add all handlers
            self.app.add_handlers(command_handlers + message_handlers)
            
            logger.debug(
                f"✅ Set up {len(command_handlers)} command handlers and message handlers"
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

    def _get_command_registry(self):
        """
        Get the initialized command registry.
        
        Returns:
            Command registry instance
            
        Raises:
            RuntimeError: When command registry is not accessible
        """
        from kickai.core.command_registry_initializer import get_initialized_command_registry
        
        try:
            registry = get_initialized_command_registry()
            all_commands = registry.list_all_commands()
            logger.info(f"✅ Command registry initialized with {len(all_commands)} commands")
            return registry
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

    def _create_command_handlers(self, registry):
        """
        Create command handlers from registry.
        
        Args:
            registry: Command registry instance
            
        Returns:
            List of command handlers
        """
        command_handlers = []
        
        # ALL commands use agentic routing - no dedicated handlers
        # This ensures single source of truth and consistent processing
        for cmd_metadata in registry.list_all_commands():
            # Use the generic agentic handler for all commands
            def create_handler(cmd_name):
                return lambda update, context: self._handle_registered_command(
                    update, context, cmd_name
                )

            handler = create_handler(cmd_metadata.name)
            command_handlers.append(CommandHandler(cmd_metadata.name.lstrip("/"), handler))
            logger.debug(f"✅ Registered agentic command handler: {cmd_metadata.name}")
        
        return command_handlers

    def _create_message_handlers(self):
        """
        Create message handlers for natural language, contact sharing, and new chat members.
        
        Returns:
            List of message handlers
        """
        # Add message handler for natural language processing
        message_handler = MessageHandler(
            filters.TEXT & ~filters.COMMAND, self._handle_natural_language_message
        )

        # Add contact handler for phone number sharing
        contact_handler = MessageHandler(filters.CONTACT, self._handle_contact_share)

        # Add new chat members handler for invite link processing
        new_chat_members_handler = MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS, self._handle_new_chat_members
        )

        # Add debug handler to log all updates
        debug_handler = MessageHandler(filters.ALL, self._debug_handler)
        
        return [message_handler, contact_handler, new_chat_members_handler, debug_handler]

    def _setup_fallback_handlers(self) -> None:
        """
        Set up fallback handlers when command registry fails.
        
        Provides minimal functionality when the command registry is not available.
        Only handles natural language messages, contact sharing, and new chat members.
        """
        try:
            # All messages now use agentic routing - minimal fallback
            handlers = [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, self._handle_natural_language_message
                ),
                MessageHandler(filters.CONTACT, self._handle_contact_share),
                MessageHandler(
                    filters.StatusUpdate.NEW_CHAT_MEMBERS, self._handle_new_chat_members
                ),
            ]

            self.app.add_handlers(handlers)
            logger.debug(f"✅ Set up {len(handlers)} fallback handlers")

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

    async def _handle_new_chat_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle new chat members joining via invite links."""
        try:
            logger.info(f"👥 New chat members event detected in chat {update.effective_chat.id}")
            
            # Validate the update has new chat members
            if not update.message or not update.message.new_chat_members:
                logger.warning("❌ No new chat members found in update")
                return
            
            # Process each new member
            for member in update.message.new_chat_members:
                if member.is_bot:
                    logger.info(f"🤖 Skipping bot member: {member.username or member.id}")
                    continue
                
                logger.info(f"👤 Processing new member: {member.first_name} (@{member.username}, ID: {member.id})")
                
                # Check if this is an invite link join
                invite_link = None
                if update.message.invite_link:
                    invite_link = update.message.invite_link.invite_link
                    logger.info(f"🔗 Invite link detected: {invite_link}")
                
                # Process the invite link if available
                if invite_link:
                    await self._process_invite_link_join(member, invite_link, update.effective_chat.id)
                else:
                    logger.info(f"ℹ️ No invite link found for member {member.id} - standard join")
                
                # Convert to domain message and route through agentic system
                message = self.agentic_router.convert_telegram_update_to_message(update)
                
                # Add new chat members context
                message.new_chat_members = [{
                    'id': member.id,
                    'username': member.username,
                    'first_name': member.first_name,
                    'last_name': member.last_name,
                    'is_bot': member.is_bot
                } for member in update.message.new_chat_members if not member.is_bot]
                
                # Route through agentic system
                response = await self.agentic_router.route_message(message)
                
                # Send welcome response
                await self._send_response(update, response)
                
        except Exception as e:
            logger.error(f"❌ Error handling new chat members: {e}")
            await self._send_error_response(
                update, "I encountered an error processing your join request."
            )

    async def _process_invite_link_join(self, member, invite_link: str, chat_id: str):
        """Process a user joining via invite link and update player records."""
        try:
            logger.info(f"🔗 Processing invite link join for user {member.id}")
            
            # Get invite link service
            from kickai.features.communication.domain.services.invite_link_service import InviteLinkService
            from kickai.database.firebase_client import get_firebase_client
            
            database = get_firebase_client()
            invite_service = InviteLinkService(database=database, team_id=self.team_id)
            
            # Validate and use the invite link
            invite_data = await invite_service.validate_and_use_invite_link(
                invite_link=invite_link,
                user_id=str(member.id),
                username=member.username
            )
            
            if not invite_data:
                logger.warning(f"❌ Invalid or expired invite link for user {member.id}")
                return
            
            logger.info(f"✅ Valid invite link processed for user {member.id}")
            
            # Update player record with telegram_id if this is a player invite
            if invite_data.get('invite_type') == 'player' and invite_data.get('player_id'):
                await self._update_player_telegram_id(
                    player_id=invite_data['player_id'],
                    telegram_id=member.id,
                    username=member.username
                )
            # Update team member record with telegram_id if this is a team member invite
            elif invite_data.get('invite_type') == 'team_member' and invite_data.get('member_id'):
                await self._update_team_member_telegram_id(
                    member_id=invite_data['member_id'],
                    telegram_id=member.id,
                    username=member.username
                )
            
        except Exception as e:
            logger.error(f"❌ Error processing invite link join: {e}")

    async def _update_player_telegram_id(self, player_id: str, telegram_id: int, username: str = None):
        """Update player record in Firestore with telegram_id."""
        try:
            logger.info(f"🔗 Updating player {player_id} with telegram_id {telegram_id}")
            
            # Get database client
            from kickai.database.firebase_client import get_firebase_client
            from kickai.core.firestore_constants import get_team_players_collection
            
            database = get_firebase_client()
            collection_name = get_team_players_collection(self.team_id)
            
            # Update the player document
            update_data = {
                'telegram_id': telegram_id,
                'username': username,
                'status': 'active',  # Activate the player when they join via invite link
                'updated_at': datetime.now().isoformat()
            }
            
            success = await database.update_player(player_id, update_data, self.team_id)
            
            if success:
                logger.info(f"✅ Successfully updated player {player_id} with telegram_id {telegram_id}")
            else:
                logger.error(f"❌ Failed to update player {player_id} with telegram_id {telegram_id}")
                
        except Exception as e:
            logger.error(f"❌ Error updating player telegram_id: {e}")

    async def _update_team_member_telegram_id(self, member_id: str, telegram_id: int, username: str = None):
        """Update team member record in Firestore with telegram_id."""
        try:
            logger.info(f"🔗 Updating team member {member_id} with telegram_id {telegram_id}")
            
            # Get database client
            from kickai.database.firebase_client import get_firebase_client
            from kickai.features.team_administration.domain.entities.team_member import TeamMember
            
            database = get_firebase_client()
            
            # Get the team member by member_id
            team_member = await database.get_team_member_by_id(member_id, self.team_id)
            if not team_member:
                logger.error(f"❌ Team member {member_id} not found in team {self.team_id}")
                return
            
            # Update the team member with telegram_id and activate them
            team_member.telegram_id = telegram_id
            if username:
                team_member.username = username
            team_member.status = "active"  # Activate the team member when they join via invite link
            team_member.updated_at = datetime.now()
            
            # Update the team member in the database
            success = await database.update_team_member(team_member)
            
            if success:
                logger.info(f"✅ Successfully updated team member {member_id} with telegram_id {telegram_id}")
            else:
                logger.error(f"❌ Failed to update team member {member_id} with telegram_id {telegram_id}")
                
        except Exception as e:
            logger.error(f"❌ Error updating team member telegram_id: {e}")

    def _determine_chat_type(self, chat_id: str) -> ChatType:
        """
        Determine the chat type based on chat ID.
        
        Args:
            chat_id: The chat ID to determine the type for
            
        Returns:
            ChatType: The type of chat (MAIN, LEADERSHIP, or PRIVATE)
        """
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
            
            logger.debug(f"🔍 Message: {formatted_text[:MESSAGE_PREVIEW_LENGTH]}...")

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
            logger.info(f"🔍 Bot token: {self.token[:TOKEN_DISPLAY_LENGTH]}...")
            logger.info(f"🔍 Main chat ID: {self.main_chat_id}")
            logger.info(f"🔍 Leadership chat ID: {self.leadership_chat_id}")

            # Start polling with basic parameters
            await self.app.updater.start_polling(
                poll_interval=POLL_INTERVAL,
                timeout=POLL_TIMEOUT,
                bootstrap_retries=BOOTSTRAP_RETRIES,
            )
            self._running = True
            logger.info("Telegram bot polling started.")

            # Test bot connection
            try:
                bot_info = await self.app.bot.get_me()
                logger.info(f"✅ Bot connected successfully: @{bot_info.username} (ID: {bot_info.id})")
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
                    logger.info(f"🔍 DEBUG: Text: {update.effective_message.text[:MESSAGE_PREVIEW_LENGTH]}...")
        except Exception as e:
            logger.error(f"❌ Error in debug handler: {e}")

    async def send_message(self, chat_id: Union[int, str], text: str, **kwargs):
        """
        Send a message to a specific chat in plain text.
        
        Args:
            chat_id: The chat ID to send the message to
            text: The message text (should be clean, formatted plain text)
            **kwargs: Additional arguments for the Telegram API
            
        Raises:
            Exception: When message sending fails
        """
        try:
            logger.info(f"Sending plain text message to chat_id={chat_id}: {text}")
            
            # Send as plain text (no parse_mode)
            await self.app.bot.send_message(
                chat_id=chat_id, 
                text=text, 
                parse_mode=None,  # Explicitly set to None for plain text
                **kwargs
            )
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            raise

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
