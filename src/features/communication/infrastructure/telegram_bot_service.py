import os
from typing import Union, Optional
from loguru import logger
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from features.communication.domain.interfaces.telegram_bot_service_interface import TelegramBotServiceInterface
from features.system_infrastructure.domain.services.permission_service import PermissionContext, get_permission_service
from core.enums import ChatType
import re

class TelegramBotService(TelegramBotServiceInterface):
    def __init__(self, token: str, team_id: str, main_chat_id: str = None, leadership_chat_id: str = None, crewai_system = None):
        self.token = token
        self.team_id = team_id
        self.main_chat_id = main_chat_id
        self.leadership_chat_id = leadership_chat_id
        self.crewai_system = crewai_system
        if not self.token:
            raise ValueError("TelegramBotService: token must be provided explicitly (not from env)")
        self.app = Application.builder().token(self.token).build()
        self._running = False
        self._setup_handlers()

    def _setup_handlers(self):
        """Set up message handlers for the Telegram bot using command registry."""
        try:
            from src.core.command_registry import get_command_registry
            
            # Get command registry (auto-discovery should be done during initialization)
            registry = get_command_registry()
            # Ensure commands are discovered if not already done
            if not registry._discovered:
                logger.info("🔍 Auto-discovering commands in telegram bot service...")
                registry.auto_discover_commands()
            
            # Get all registered commands
            all_commands = registry.list_all_commands()
            
            # Set up command handlers from registry
            command_handlers = []
            
            # ALL commands use CrewAI agents - no dedicated handlers
            # This ensures single source of truth and consistent processing
            dedicated_handlers = {}
            
            for cmd_metadata in all_commands:
                # Check if this command has a dedicated handler
                if cmd_metadata.name in dedicated_handlers:
                    # Use the dedicated handler
                    handler = dedicated_handlers[cmd_metadata.name]
                    command_handlers.append(CommandHandler(cmd_metadata.name.lstrip('/'), handler))
                    logger.info(f"✅ Registered dedicated command handler: {cmd_metadata.name}")
                else:
                    # Use the generic CrewAI handler
                    def create_handler(cmd_name):
                        return lambda update, context: self._handle_registered_command(update, context, cmd_name)
                    
                    handler = create_handler(cmd_metadata.name)
                    command_handlers.append(CommandHandler(cmd_metadata.name.lstrip('/'), handler))
                    logger.info(f"✅ Registered CrewAI command handler: {cmd_metadata.name}")
            
            # Add message handler for natural language processing
            message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_natural_language_message)
            
            # Add all handlers to the application
            self.app.add_handlers(command_handlers + [message_handler])
            
            logger.info(f"✅ Set up {len(command_handlers)} command handlers and 1 message handler")
            
        except Exception as e:
            logger.error(f"❌ Error setting up handlers: {e}")
            # Fallback to basic handlers
            self._setup_fallback_handlers()
    
    def _setup_fallback_handlers(self):
        """Set up fallback handlers when command registry fails."""
        try:
            # All commands now use CrewAI agents - minimal fallback
            handlers = [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_natural_language_message)
            ]
            
            self.app.add_handlers(handlers)
            logger.info(f"✅ Set up {len(handlers)} fallback handlers")
            
        except Exception as e:
            logger.error(f"❌ Error setting up fallback handlers: {e}")

    async def _handle_natural_language_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle natural language messages using CrewAI processing."""
        try:
            user_id = str(update.effective_user.id)
            message_text = update.message.text.strip()
            chat_id = str(update.effective_chat.id)
            username = update.effective_user.username or update.effective_user.first_name
            
            # Determine chat type
            chat_type = self._determine_chat_type(chat_id)
            
            logger.info(f"📨 Natural language message from {username} ({user_id}) in {chat_type.value}: '{message_text}'")
            
            # Check for help-related keywords first (bypass registration check)
            message_lower = message_text.lower()
            if "help" in message_lower:
                logger.info(f"📨 Help keyword detected in natural language: '{message_text}'")
                # Delegate to CrewAI processing for help requests
                await self._handle_crewai_processing(update, message_text, user_id, chat_id, chat_type, username)
                return
            
            # Check if user is registered (only for main chat)
            if chat_type == ChatType.MAIN:
                is_registered = await self._check_user_registration(user_id)
                if not is_registered:
                    # User not registered - show leadership contact message
                    await self._show_leadership_contact_message(update, username)
                    return
            elif chat_type == ChatType.LEADERSHIP:
                # Check if this is the first user in leadership chat
                is_first_user = await self._check_if_first_user()
                if is_first_user:
                    # First user - show registration message
                    logger.info(f"🎉 First user detected in leadership chat (natural language): {username}")
                    await self._show_first_user_registration_message(update, username)
                    return
                else:
                    # Check if user is registered as team member
                    is_registered = await self._check_user_registration(user_id)
                    if not is_registered:
                        # User not registered - show first user message
                        logger.info(f"👤 Unregistered user in leadership chat: {username}")
                        await self._show_first_user_registration_message(update, username)
                        return
            
            # User is registered or in leadership chat - process with CrewAI
            await self._handle_crewai_processing(update, message_text, user_id, chat_id, chat_type, username)
            
        except Exception as e:
            logger.error(f"❌ Error handling natural language message: {e}")
            await self._send_error_response(update, "I encountered an error processing your message. Please try again.")

    def _determine_chat_type(self, chat_id: str) -> ChatType:
        """Determine the chat type based on chat ID."""
        if chat_id == self.main_chat_id:
            return ChatType.MAIN
        elif chat_id == self.leadership_chat_id:
            return ChatType.LEADERSHIP
        else:
            return ChatType.PRIVATE

    async def _handle_registered_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, command_name: str):
        """Handle registered commands by delegating to CrewAI system."""
        try:
            user_id = str(update.effective_user.id)
            chat_id = str(update.effective_chat.id)
            chat_type = self._determine_chat_type(chat_id)
            username = update.effective_user.username or update.effective_user.first_name
            
            # Build the full command with arguments
            args = context.args if context.args else []
            message_text = f"{command_name} {' '.join(args)}".strip()
            
            logger.info(f"📨 Registered command from {username} ({user_id}) in {chat_type.value}: '{message_text}'")
            
            # Check if this is the first user in leadership chat (for any command)
            if chat_type == ChatType.LEADERSHIP:
                is_first_user = await self._check_if_first_user()
                if is_first_user:
                    logger.info(f"🎉 First user detected in leadership chat: {username}")
                    await self._show_first_user_registration_message(update, username)
                    return  # Block normal command processing
            
            # Delegate to CrewAI processing
            await self._handle_crewai_processing(update, message_text, user_id, chat_id, chat_type, username)
            
        except Exception as e:
            logger.error(f"❌ Error handling registered command {command_name}: {e}")
            await self._send_error_response(update, "I encountered an error processing your command. Please try again.")

    async def _handle_crewai_processing(self, update: Update, message_text: str, 
                                      user_id: str, chat_id: str, chat_type: ChatType, username: str):
        """Handle message processing with CrewAI system."""
        try:
            # Debug logging
            logger.info(f"🔍 CREWAI DEBUG: message_text='{message_text}'")
            logger.info(f"🔍 CREWAI DEBUG: crewai_system available: {self.crewai_system is not None}")
            logger.info(f"🔍 CREWAI DEBUG: crewai_system type: {type(self.crewai_system).__name__}")
            logger.info(f"🔍 CREWAI DEBUG: crewai_system has execute_task: {hasattr(self.crewai_system, 'execute_task')}")
            
            if not self.crewai_system:
                logger.warning("CrewAI system not available, using fallback")
                await self._handle_fallback_response(update, message_text)
                return
            
            # Check if message text is empty
            if not message_text or message_text.strip() == "":
                logger.error(f"❌ Error in CrewAI processing: Message text is empty")
                await self._handle_fallback_response(update, "I received an empty message. Please try again.")
                return
            
            # Create execution context
            execution_context = {
                'user_id': user_id,
                'team_id': self.team_id,
                'chat_id': chat_id,
                'is_leadership_chat': chat_type == ChatType.LEADERSHIP,
                'username': username,
                'message_text': message_text
            }
            
            logger.info(f"🔍 CREWAI DEBUG: About to call execute_task with message_text='{message_text}'")
            logger.info(f"🔍 CREWAI DEBUG: crewai_system type: {type(self.crewai_system).__name__}")
            logger.info(f"🔍 CREWAI DEBUG: crewai_system has execute_task: {hasattr(self.crewai_system, 'execute_task')}")
            logger.info(f"🔍 CREWAI DEBUG: crewai_system methods: {[method for method in dir(self.crewai_system) if not method.startswith('_')]}")
            logger.info(f"🔍 CREWAI DEBUG: execution_context={execution_context}")
            # Execute with CrewAI
            if hasattr(self.crewai_system, 'execute_task'):
                logger.info(f"🔍 CREWAI DEBUG: Calling execute_task method")
                result = await self.crewai_system.execute_task(message_text, execution_context)
            else:
                logger.error(f"🔍 CREWAI DEBUG: execute_task method not found!")
                result = "❌ System error: execute_task method not available"
            
            logger.info(f"🔍 CREWAI DEBUG: execute_task returned: '{result[:100]}...'")
            
            # Safely escape the result for Telegram Markdown
            safe_result = self._escape_markdown(result)
            
            await update.message.reply_text(safe_result, parse_mode='Markdown')
            logger.info(f"✅ CrewAI processing completed for user {username}")
            
        except Exception as e:
            logger.error(f"❌ Error in CrewAI processing: {e}")
            await self._handle_fallback_response(update, message_text)

    async def _handle_fallback_response(self, update: Update, message_text: str):
        """Handle fallback responses when CrewAI is not available."""
        try:
            message_lower = message_text.lower()
            chat_id = str(update.effective_chat.id)
            chat_type = self._determine_chat_type(chat_id)
            username = update.effective_user.username or update.effective_user.first_name
            
            # Registration-related queries
            if any(word in message_lower for word in ["register", "registration", "join", "sign up", "add me"]):
                if chat_type == ChatType.MAIN:
                    await self._show_leadership_contact_message(update, username)
                elif chat_type == ChatType.LEADERSHIP:
                    response = (
                        "👔 *Leadership Registration*\n\n"
                        "To register a new player:\n"
                        "• Use `/register [name] [phone] [position]`\n"
                        "• Example: `/register John Smith +1234567890 Forward`\n\n"
                        "To register yourself as a team member:\n"
                        "• Use `/register` to start the process\n\n"
                        "Need help? Ask me anything!"
                    )
                    await update.message.reply_text(response, parse_mode='Markdown')
                else:
                    await self._handle_private_registration(update, username)
                return
            
            # Help-related queries
            elif "help" in message_lower:
                response = (
                    "🤖 *KICKAI Help*\n\n"
                    "*Available Commands:*\n"
                    "• /start - Welcome message\n"
                    "• /help - Show this help\n"
                    "• /register - Register as a player\n"
                    "• /myinfo - Check your information\n"
                    "• /list - List team members\n"
                    "• /status [phone] - Check player status\n\n"
                    "You can also ask me questions in natural language!"
                )
                await update.message.reply_text(response, parse_mode='Markdown')
                return
            
            # Greeting queries
            elif any(word in message_lower for word in ["hello", "hi", "hey"]):
                response = "👋 Hello! I'm KICKAI, your football team assistant. How can I help you today?"
                await update.message.reply_text(response, parse_mode='Markdown')
                return
            
            # Default response
            else:
                response = "🤖 I'm KICKAI, your football team assistant. Use /help to see what I can do!"
                await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error in fallback response: {e}")
            await self._send_error_response(update, "I'm having trouble processing your message right now.")

    async def _send_error_response(self, update: Update, error_message: str):
        """Send an error response to the user."""
        try:
            await update.message.reply_text(f"❌ {error_message}")
        except Exception as e:
            logger.error(f"❌ Error sending error response: {e}")

    # Note: All dedicated command handlers have been removed
    # All commands now use CrewAI agents for consistent processing

    # Note: All dedicated command handlers have been removed
    # All commands now use CrewAI agents for consistent processing

    # Note: All dedicated command handlers have been removed
    # All commands now use CrewAI agents for consistent processing

    # Note: All dedicated command handlers have been removed
    # All commands now use CrewAI agents for consistent processing

    # Note: /help command is now handled by CrewAI system via HelpAssistantAgent
    # The dedicated handler has been removed to ensure all help requests go through the agent system

    # Note: All dedicated command handlers have been removed
    # All commands now use CrewAI agents for consistent processing

    async def _handle_first_user_registration(self, update: Update, user_id: str, username: str):
        """Handle first user registration in leadership chat."""
        try:
            message_text = update.message.text.strip()
            
            # Parse registration command: /register [name] [phone] [role]
            # Handle names with spaces by looking for phone number pattern
            import re
            
            # Remove /register from the beginning
            content = message_text.replace('/register', '').strip()
            
            # Find phone number (starts with + and contains digits)
            phone_match = re.search(r'\+[\d\s\-\(\)]+', content)
            if not phone_match:
                # No phone number found - show help
                await self._show_first_user_registration_message(update, username)
                return
            
            phone = phone_match.group().strip()
            phone_start = phone_match.start()
            phone_end = phone_match.end()
            
            # Extract name (everything before phone)
            name = content[:phone_start].strip()
            
            # Extract role (everything after phone)
            role = content[phone_end:].strip()
            
            # Validate we have all required parts
            if not name or not phone or not role:
                await self._show_first_user_registration_message(update, username)
                return
            
            logger.info(f"🔍 First user registration: name='{name}', phone='{phone}', role='{role}'")
            
            # Get services
            from core.dependency_container import get_service
            from features.team_administration.domain.services.team_service import TeamService
            from features.team_administration.domain.entities.team_member import TeamMember
            
            team_service = get_service(TeamService)
            
            # Create team member directly using the entity
            team_member = TeamMember(
                user_id=user_id,
                name=name,  # Add the parsed name
                phone=phone,  # Add the parsed phone
                telegram_id=user_id,
                telegram_username=username,
                team_id=self.team_id,
                roles=["admin"],  # First user is always admin
                permissions=["manage_team", "manage_players", "manage_matches", "manage_finances"],
                chat_access={"main_chat": True, "leadership_chat": True}
            )
            
            # Save team member to database
            saved_team_member = await team_service.team_repository.create_team_member(team_member)
            
            logger.info(f"✅ Team member created and saved to database: {saved_team_member.to_dict()}")
            
            # Send success message
            success_message = (
                f"🎉 *Welcome to KICKAI, {name}!*\n\n"
                f"✅ **Registration Successful!**\n\n"
                f"👑 **You are now the team administrator** with full access to:\n"
                f"• Player management and registration\n"
                f"• Team configuration and settings\n"
                f"• Match scheduling and management\n"
                f"• Financial oversight and reporting\n\n"
                f"📋 **Your Details:**\n"
                f"• **Name:** {name}\n"
                f"• **Phone:** {phone}\n"
                f"• **Role:** {role}\n"
                f"• **Status:** Active Administrator\n\n"
                f"🚀 **What you can do now:**\n"
                f"• Use /help to see all available commands\n"
                f"• Add other team members using /add command\n"
                f"• Generate invite links for players\n"
                f"• Manage the entire team system\n\n"
                f"Welcome aboard! 🏆"
            )
            
            await update.message.reply_text(success_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error in first user registration: {e}")
            await self._send_error_response(update, "I encountered an error during registration. Please try again.")

    async def _handle_main_chat_registration(self, update: Update, user_id: str, username: str):
        """Handle registration in main chat - check if user needs to be added by leadership."""
        try:
            # Check if user is already registered in the system
            is_registered = await self._check_user_registration(user_id)
            
            if is_registered:
                # User is already registered - show their info and offer to update
                await self._show_registered_user_info(update, user_id, username)
            else:
                # User needs to be added by leadership
                await self._show_leadership_contact_message(update, username)
                
        except Exception as e:
            logger.error(f"❌ Error in main chat registration: {e}")
            await self._show_leadership_contact_message(update, username)

    async def _check_user_registration(self, user_id: str) -> bool:
        """Check if user is already registered in the system."""
        try:
            # Get services from dependency container
            from core.dependency_container import get_service
            from features.player_registration.domain.services.player_service import PlayerService
            from features.team_administration.domain.services.team_service import TeamService
            
            player_service = get_service(PlayerService)
            team_service = get_service(TeamService)
            
            # Check if user exists as a player
            try:
                # Try to get player by Telegram user ID
                player = await player_service.get_player_by_telegram_id(user_id, self.team_id)
                if player:
                    logger.info(f"✅ User {user_id} found as registered player")
                    return True
            except Exception as e:
                logger.debug(f"User {user_id} not found as player: {e}")
            
            # Check if user exists as a team member
            try:
                # Try to get team member by Telegram user ID
                team_member = await team_service.get_team_member_by_telegram_id(self.team_id, user_id)
                if team_member:
                    logger.info(f"✅ User {user_id} found as team member")
                    return True
            except Exception as e:
                logger.debug(f"User {user_id} not found as team member: {e}")
            
            logger.info(f"❌ User {user_id} not registered in the system")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking user registration: {e}")
            return False

    async def _check_if_first_user(self) -> bool:
        """Check if this is the first user in the system (no team members exist)."""
        try:
            from core.dependency_container import get_service
            from features.team_administration.domain.services.team_service import TeamService
            
            team_service = get_service(TeamService)
            
            # Get all team members
            team_members = await team_service.get_team_members(self.team_id)
            
            # If no team members exist, this is the first user
            is_first_user = len(team_members) == 0
            
            logger.info(f"🔍 First user check: {len(team_members)} team members found, is_first_user={is_first_user}")
            return is_first_user
            
        except Exception as e:
            logger.error(f"❌ Error checking if first user: {e}")
            return False

    async def _show_first_user_registration_message(self, update: Update, username: str):
        """Show message for first user registration in leadership chat."""
        try:
            message = (
                f"🎉 *Welcome to KICKAI, {username}!*\n\n"
                f"🌟 **You are the first user in this leadership chat!**\n\n"
                f"👑 **You will be set up as the team administrator** with full access to:\n"
                f"• Player management and registration\n"
                f"• Team configuration and settings\n"
                f"• Match scheduling and management\n"
                f"• Financial oversight and reporting\n\n"
                f"📝 **To complete your setup, please provide your details:**\n\n"
                f"Use the command:\n"
                f"`/register [Your Full Name] [Your Phone Number] [Your Role]`\n\n"
                f"**Example:**\n"
                f"`/register John Smith +1234567890 Team Manager`\n\n"
                f"💡 **Your role can be:**\n"
                f"• Team Manager, Coach, Assistant Coach\n"
                f"• Club Administrator, Treasurer\n"
                f"• Volunteer Coordinator, etc.\n\n"
                f"🚀 **Once registered, you can:**\n"
                f"• Add other team members and players\n"
                f"• Generate invite links for chats\n"
                f"• Manage the entire team system\n\n"
                f"Ready to get started? Use the /register command above!"
            )
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error showing first user registration message: {e}")
            await self._send_error_response(update, "I encountered an error processing your request.")

    async def _show_registered_user_info(self, update: Update, user_id: str, username: str):
        """Show registered user information and offer to update."""
        try:
            message = (
                f"👋 *Welcome back, {username}!*\n\n"
                f"✅ You are already registered as a player in the team.\n\n"
                f"📋 *Your Information:*\n"
                f"• **User ID:** {user_id}\n"
                f"• **Username:** {username}\n"
                f"• **Status:** Active Player\n\n"
                f"💡 *Need to update your information?*\n"
                f"Contact the team leadership to make any changes.\n\n"
                f"🎯 *What you can do:*\n"
                f"• Use /myinfo to check your details\n"
                f"• Use /list to see team members\n"
                f"• Use /status to check your availability\n"
                f"• Ask me questions in natural language!"
            )
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error showing registered user info: {e}")
            await self._send_error_response(update, "I encountered an error retrieving your information.")

    async def _show_leadership_contact_message(self, update: Update, username: str):
        """Show message directing user to contact team leadership."""
        try:
            message = (
                f"👋 *Welcome, {username}!*\n\n"
                f"🎯 *To join the team as a player:*\n\n"
                f"📞 **Contact Team Leadership**\n"
                f"You need to be added as a player by someone in the team's leadership.\n\n"
                f"💬 **What to do:**\n"
                f"1. Reach out to someone in the team's leadership chat\n"
                f"2. Ask them to add you as a player using the `/add` command\n"
                f"3. They'll send you an invite link to join the main chat\n"
                f"4. Once added, you can register with your full details\n\n"
                f"❓ **Got here by mistake?**\n"
                f"If you're not interested in joining the team, you can leave this chat.\n\n"
                f"🤖 *Need help?*\n"
                f"Use /help to see available commands or ask me questions!"
            )
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error showing leadership contact message: {e}")
            await self._send_error_response(update, "I encountered an error processing your request.")

    async def _handle_private_registration(self, update: Update, username: str):
        """Handle registration in private chat - provide guidance."""
        try:
            message = (
                f"👋 *Hi {username}!*\n\n"
                f"🤖 *Registration Guidance*\n\n"
                f"📋 *To join the team:*\n\n"
                f"🎯 *Player Registration* (Main Chat):\n"
                f"• Join the main team chat\n"
                f"• Use /register to start the process\n"
                f"• Requires team leadership approval\n\n"
                f"👔 *Team Member Registration* (Leadership Chat):\n"
                f"• Join the leadership chat\n"
                f"• Use /register for team member setup\n"
                f"• For coaches, managers, volunteers\n\n"
                f"💡 *Need help?*\n"
                f"Contact the team leadership to be added to the appropriate chat."
            )
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error in private registration: {e}")
            await self._send_error_response(update, "I encountered an error providing registration guidance.")

    def _get_crewai_system(self):
        """Get the CrewAI system for processing."""
        if self.crewai_system:
            return self.crewai_system
        # Use the new YAML-based crew
        from crew import get_kickai_crew
        return get_kickai_crew()

    async def start_polling(self) -> None:
        """Start the bot polling."""
        try:
            logger.info("Starting Telegram bot polling...")
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()
            self._running = True
            logger.info("Telegram bot polling started.")
        except Exception as e:
            logger.error(f"❌ Error starting bot polling: {e}")
            raise

    async def send_message(self, chat_id: Union[int, str], text: str, **kwargs):
        """Send a message to a specific chat."""
        try:
            logger.info(f"Sending message to chat_id={chat_id}: {text}")
            await self.app.bot.send_message(chat_id=chat_id, text=text, **kwargs)
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            raise

    def _escape_markdown(self, text: str) -> str:
        """Escape special characters for Telegram MarkdownV2 parsing."""
        if not text:
            return text
        
        import re
        
        # For Telegram MarkdownV2, we need to be more careful about escaping
        # The key is to preserve intentional markdown while escaping problematic characters
        
        # First, let's handle the text in a way that preserves formatting
        # Convert common markdown patterns to Telegram MarkdownV2 format
        
        # Convert **bold** to __bold__ (Telegram MarkdownV2 uses double underscores)
        text = re.sub(r'\*\*(.*?)\*\*', r'__\1__', text)
        
        # Convert *italic* to _italic_ (but be careful not to break existing patterns)
        # Only convert single asterisks that aren't part of bold patterns
        text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'_\1_', text)
        
        # Now we need to escape characters that are not part of markdown formatting
        # Characters to escape: [ ] ( ) ~ ` > # + = | { } . !
        # Characters to preserve: _ * (for markdown), - (for lists), / (for commands)
        
        escape_chars = ['[', ']', '(', ')', '~', '`', '>', '#', '+', '=', '|', '{', '}', '.', '!']
        
        escaped_text = text
        for char in escape_chars:
            escaped_text = escaped_text.replace(char, f'\\{char}')
        
        return escaped_text



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