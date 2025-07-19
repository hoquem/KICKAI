import os
from typing import Union, Optional
from loguru import logger
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from features.communication.domain.interfaces.telegram_bot_service_interface import TelegramBotServiceInterface
from features.system_infrastructure.domain.services.permission_service import PermissionContext, get_permission_service
from enums import ChatType
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
        """Set up message handlers for the Telegram bot."""
        try:
            # Command handlers (highest priority)
            command_handlers = [
                ("start", self._handle_start_command),
                ("help", self._handle_help_command),
                ("register", self._handle_register_command),
                ("myinfo", self._handle_myinfo_command),
                ("list", self._handle_list_command),
                ("status", self._handle_status_command),
            ]
            
            for command, handler in command_handlers:
                self.app.add_handler(CommandHandler(command, handler))
            
            # Natural language handler (for non-command text messages)
            self.app.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                self._handle_natural_language_message
            ))
            
            logger.info(f"✅ Telegram bot handlers set up for team {self.team_id}")
            logger.info(f"   - Text message handler: ✅")
            logger.info(f"   - Command handlers: ✅")
            
        except Exception as e:
            logger.error(f"❌ Error setting up handlers: {e}")
            raise

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
                # Use the same help logic as the /help command
                if chat_type == ChatType.LEADERSHIP:
                    help_message = (
                        "👔 *KICKAI Leadership Commands*\n\n"
                        "*Player Management:*\n"
                        "• /register [name] [phone] [position] - Register new player\n"
                        "• /list - List all players with status\n"
                        "• /status [phone] - Check player status\n\n"
                        "*Team Management:*\n"
                        "• /myinfo - Check your admin info\n\n"
                        "*Natural Language:*\n"
                        "You can also ask me questions in natural language!"
                    )
                else:
                    help_message = (
                        "🤖 *KICKAI Commands*\n\n"
                        "*Player Commands:*\n"
                        "• /start - Welcome message\n"
                        "• /help - Show this help\n"
                        "• /register - Register as a player\n"
                        "• /myinfo - Check your information\n"
                        "• /list - List team members\n"
                        "• /status [phone] - Check player status\n\n"
                        "*Natural Language:*\n"
                        "You can also ask me questions in natural language!"
                    )
                
                await update.message.reply_text(help_message, parse_mode='Markdown')
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
                    await self._show_first_user_registration_message(update, username)
                    return
                else:
                    # Check if user is registered as team member
                    is_registered = await self._check_user_registration(user_id)
                    if not is_registered:
                        # User not registered - show first user message
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

    async def _handle_crewai_processing(self, update: Update, message_text: str, 
                                      user_id: str, chat_id: str, chat_type: ChatType, username: str):
        """Handle message processing with CrewAI system."""
        try:
            if not self.crewai_system:
                logger.warning("CrewAI system not available, using fallback")
                await self._handle_fallback_response(update, message_text)
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
            
            # Execute with CrewAI
            result = await self.crewai_system.execute_task(message_text, execution_context)
            
            await update.message.reply_text(result, parse_mode='Markdown')
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

    async def _handle_myinfo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /myinfo command."""
        try:
            user_id = str(update.effective_user.id)
            username = update.effective_user.username or update.effective_user.first_name
            chat_id = str(update.effective_chat.id)
            chat_type = self._determine_chat_type(chat_id)
            
            logger.info(f"✅ MyInfo command handled for user {user_id} in {chat_type.value}")
            
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
                    await self._show_first_user_registration_message(update, username)
                    return
                else:
                    # Check if user is registered as team member
                    is_registered = await self._check_user_registration(user_id)
                    if not is_registered:
                        # User not registered - show first user message
                        await self._show_first_user_registration_message(update, username)
                        return
            
            # User is registered or in leadership chat - process with CrewAI
            await self._handle_crewai_processing(
                update, "/myinfo", user_id, chat_id, chat_type, username
            )
            
        except Exception as e:
            logger.error(f"❌ Error handling myinfo command: {e}")
            await self._send_error_response(update, "I encountered an error processing your request.")

    async def _handle_list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command."""
        try:
            user_id = str(update.effective_user.id)
            username = update.effective_user.username or update.effective_user.first_name
            chat_id = str(update.effective_chat.id)
            chat_type = self._determine_chat_type(chat_id)
            
            logger.info(f"✅ List command handled for user {user_id} in {chat_type.value}")
            
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
                    await self._show_first_user_registration_message(update, username)
                    return
                else:
                    # Check if user is registered as team member
                    is_registered = await self._check_user_registration(user_id)
                    if not is_registered:
                        # User not registered - show first user message
                        await self._show_first_user_registration_message(update, username)
                        return
            
            # User is registered or in leadership chat - process with CrewAI
            await self._handle_crewai_processing(
                update, "/list", user_id, chat_id, chat_type, username
            )
            
        except Exception as e:
            logger.error(f"❌ Error handling list command: {e}")
            await self._send_error_response(update, "I encountered an error processing your request.")

    async def _handle_status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        try:
            user_id = str(update.effective_user.id)
            username = update.effective_user.username or update.effective_user.first_name
            message_text = update.message.text.strip()
            chat_id = str(update.effective_chat.id)
            chat_type = self._determine_chat_type(chat_id)
            
            logger.info(f"✅ Status command handled for user {user_id} in {chat_type.value}")
            
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
                    await self._show_first_user_registration_message(update, username)
                    return
                else:
                    # Check if user is registered as team member
                    is_registered = await self._check_user_registration(user_id)
                    if not is_registered:
                        # User not registered - show first user message
                        await self._show_first_user_registration_message(update, username)
                        return
            
            # User is registered or in leadership chat - process with CrewAI
            await self._handle_crewai_processing(
                update, message_text, user_id, chat_id, chat_type, username
            )
            
        except Exception as e:
            logger.error(f"❌ Error handling status command: {e}")
            await self._send_error_response(update, "I encountered an error processing your request.")

    async def _handle_start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        try:
            user_id = str(update.effective_user.id)
            username = update.effective_user.username or update.effective_user.first_name
            
            logger.info(f"✅ Start command handled for user {user_id}")
            
            welcome_message = (
                f"👋 Welcome to *KICKAI* for *{self.team_id}*!\n\n"
                f"🤖 I'm your AI-powered football team assistant.\n"
                f"• Organize matches, manage attendance, and more.\n"
                f"• Use /help to see what you can do!\n\n"
                f"Let's kick off a smarter season! ⚽️"
            )
            
            await update.message.reply_text(welcome_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error handling start command: {e}")
            await self._send_error_response(update, "I encountered an error processing your request.")

    async def _handle_help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        try:
            user_id = str(update.effective_user.id)
            username = update.effective_user.username or update.effective_user.first_name
            chat_id = str(update.effective_chat.id)
            chat_type = self._determine_chat_type(chat_id)
            
            logger.info(f"✅ Help command handled for user {user_id} in {chat_type.value}")
            
            if chat_type == ChatType.LEADERSHIP:
                help_message = (
                    "👔 *KICKAI Leadership Commands*\n\n"
                    "*Player Management:*\n"
                    "• /register [name] [phone] [position] - Register new player\n"
                    "• /list - List all players with status\n"
                    "• /status [phone] - Check player status\n\n"
                    "*Team Management:*\n"
                    "• /myinfo - Check your admin info\n\n"
                    "*Natural Language:*\n"
                    "You can also ask me questions in natural language!"
                )
            else:
                help_message = (
                    "🤖 *KICKAI Commands*\n\n"
                    "*Player Commands:*\n"
                    "• /start - Welcome message\n"
                    "• /help - Show this help\n"
                    "• /register - Register as a player\n"
                    "• /myinfo - Check your information\n"
                    "• /list - List team members\n"
                    "• /status [phone] - Check player status\n\n"
                    "*Natural Language:*\n"
                    "You can also ask me questions in natural language!"
                )
            
            await update.message.reply_text(help_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error handling help command: {e}")
            await self._send_error_response(update, "I encountered an error processing your request.")

    async def _handle_register_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /register command."""
        try:
            user_id = str(update.effective_user.id)
            username = update.effective_user.username or update.effective_user.first_name
            chat_id = str(update.effective_chat.id)
            chat_type = self._determine_chat_type(chat_id)
            
            logger.info(f"✅ Register command handled for user {user_id} in {chat_type.value}")
            
            # Handle registration based on chat type
            if chat_type == ChatType.MAIN:
                await self._handle_main_chat_registration(update, user_id, username)
            elif chat_type == ChatType.LEADERSHIP:
                # Check if this is the first user in leadership chat
                is_first_user = await self._check_if_first_user()
                if is_first_user:
                    # Handle first user registration directly
                    await self._handle_first_user_registration(update, user_id, username)
                else:
                    # For subsequent users, use CrewAI for admin registration
                    await self._handle_crewai_processing(
                        update, "/register", user_id, chat_id, chat_type, username
                    )
            else:
                # Private chat - provide guidance
                await self._handle_private_registration(update, username)
            
        except Exception as e:
            logger.error(f"❌ Error handling register command: {e}")
            await self._send_error_response(update, "I encountered an error processing your request.")

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
        """Get the CrewAI system instance."""
        return self.crewai_system

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