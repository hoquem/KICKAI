import os
from typing import Union
from loguru import logger
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from features.communication.domain.interfaces.telegram_bot_service_interface import TelegramBotServiceInterface
from features.system_infrastructure.domain.services.permission_service import PermissionContext, get_permission_service
from enums import ChatType
import re

class TelegramBotService(TelegramBotServiceInterface):
    def __init__(self, token: str, team_id: str, main_chat_id: str = None, leadership_chat_id: str = None):
        self.token = token
        self.team_id = team_id
        self.main_chat_id = main_chat_id
        self.leadership_chat_id = leadership_chat_id
        if not self.token:
            raise ValueError("TelegramBotService: token must be provided explicitly (not from env)")
        self.app = Application.builder().token(self.token).build()
        self._running = False
        self._setup_handlers()

    def _setup_handlers(self):
        """Set up message handlers for the Telegram bot."""
        try:
            # Import the message handling system
            from bot_telegram.message_handling.handler import handle_message, register_simplified_handler
            from bot_telegram.command_dispatcher import get_command_dispatcher
            
            # Register the main message handler for all text messages
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text_message))
            
            # Register command handlers
            self.app.add_handler(CommandHandler("start", self._handle_start_command))
            self.app.add_handler(CommandHandler("help", self._handle_help_command))
            self.app.add_handler(CommandHandler("register", self._handle_register_command))
            
            # Register the simplified message handler
            register_simplified_handler(self.app)
            
            logger.info(f"✅ Telegram bot handlers set up for team {self.team_id}")
            logger.info(f"   - Text message handler: ✅")
            logger.info(f"   - Command handlers: ✅")
            logger.info(f"   - Simplified message handler: ✅")
            
        except Exception as e:
            logger.error(f"❌ Error setting up Telegram bot handlers: {e}")
            # Fallback to basic handler
            self.app.add_handler(CommandHandler("start", self._start))
            logger.warning("⚠️ Using fallback basic handler")

    async def _handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming text messages using a simplified approach."""
        try:
            logger.info(f"📨 Received text message from user {update.effective_user.id}: {update.message.text[:50]}...")
            
            # For now, use a simple response system
            message_text = update.message.text.strip()
            
            if "hello" in message_text.lower() or "hi" in message_text.lower():
                response = "👋 Hello! I'm KICKAI, your football team assistant. How can I help you today?"
            elif "help" in message_text.lower():
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
            elif "status" in message_text.lower():
                response = "📊 I can help you check player status. Use /status [phone] for specific players or /myinfo for your own status."
            elif "register" in message_text.lower():
                response = "📝 I can help you register as a player. Use /register to start the registration process."
            else:
                response = (
                    "🤖 Thanks for your message! I'm still learning, but I can help with:\n"
                    "• Player registration and status\n"
                    "• Team management\n"
                    "• Match organization\n"
                    "• And more!\n\n"
                    "Try /help for a full list of commands."
                )
            
            await update.message.reply_text(response, parse_mode='Markdown')
            logger.info(f"✅ Message processed and response sent")
                
        except Exception as e:
            logger.error(f"❌ Error handling text message: {e}")
            await update.message.reply_text("❌ Sorry, I encountered an error processing your message. Please try again.")

    async def _handle_start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command."""
        try:
            welcome_message = (
                f"👋 Welcome to *KICKAI*!\n\n"
                f"🤖 I'm your AI-powered football team assistant.\n"
                f"• Use /help to see what I can do\n"
                f"• Ask me questions about your team\n"
                f"• I can help with registration, matches, and more!\n\n"
                f"Let's kick off a smarter season! ⚽️"
            )
            
            await update.message.reply_text(welcome_message, parse_mode='Markdown')
            logger.info(f"✅ Start command handled for user {update.effective_user.id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling start command: {e}")
            await update.message.reply_text("❌ Sorry, I encountered an error. Please try again.")

    async def _handle_help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command with permission-based filtering."""
        try:
            # Determine chat type based on chat ID
            chat_id = str(update.effective_chat.id)
            user_id = str(update.effective_user.id)
            
            if chat_id == self.main_chat_id:
                chat_type = ChatType.MAIN
            elif chat_id == self.leadership_chat_id:
                chat_type = ChatType.LEADERSHIP
            else:
                chat_type = ChatType.PRIVATE
            
            # Create permission context
            permission_context = PermissionContext(
                user_id=user_id,
                team_id=self.team_id,
                chat_id=chat_id,
                chat_type=chat_type
            )
            
            # Get available commands from permission service
            permission_service = get_permission_service()
            available_commands = await permission_service.get_available_commands(permission_context)
            
            # Generate help text based on available commands
            if chat_type == ChatType.MAIN:
                help_text = (
                    f"🤖 *KICKAI Help - Main Chat*\n\n"
                    f"*Available Commands:*\n"
                )
            elif chat_type == ChatType.LEADERSHIP:
                help_text = (
                    f"👔 *KICKAI Help - Leadership Chat*\n\n"
                    f"*Available Commands:*\n"
                )
            else:
                help_text = (
                    f"🤖 *KICKAI Help*\n\n"
                    f"*Available Commands:*\n"
                )
            
            # Add available commands to help text
            for command in available_commands:
                if command == "/help":
                    help_text += f"• {command} - Show this help\n"
                elif command == "/start":
                    help_text += f"• {command} - Welcome message\n"
                elif command == "/register":
                    help_text += f"• {command} - Register as a player\n"
                elif command == "/myinfo":
                    help_text += f"• {command} - Check your information\n"
                elif command == "/list":
                    help_text += f"• {command} - List team members\n"
                elif command == "/status":
                    help_text += f"• {command} [phone] - Check player status\n"
                elif command == "/promote":
                    help_text += f"• {command} [player_id] - Promote team member to admin\n"
                elif command == "/updateteaminfo":
                    help_text += f"• {command} - Update team information\n"
                else:
                    help_text += f"• {command}\n"
            
            # Add contextual guidance based on user status
            user_perms = await permission_service.get_user_permissions(user_id, self.team_id)
            
            if not user_perms.is_player and not user_perms.is_team_member and not user_perms.is_admin:
                if chat_type == ChatType.MAIN:
                    help_text += f"\n To become a player, use /register\n"
                    help_text += f"❓ Need help? Contact the team leadership\n"
                elif chat_type == ChatType.LEADERSHIP:
                    help_text += f"\n To join the team, use /register\n"
                    help_text += f"❓ Need help? Contact existing team members\n"
            else:
                help_text += f"\n✅ You are registered! Use /myinfo to check your details\n"
            
            help_text += f"\n💡 You can also ask me questions in natural language!"
            
            await update.message.reply_text(help_text, parse_mode='Markdown')
            logger.info(f"✅ Help command handled for user {update.effective_user.id} in {chat_type.value}")
            
        except Exception as e:
            logger.error(f"❌ Error handling help command: {e}")
            # Fallback help message
            fallback_help = (
                f"🤖 *KICKAI Help*\n\n"
                f"*Available Commands:*\n"
                f"• /start - Welcome message\n"
                f"• /help - Show this help\n"
                f"• /register - Register as a player\n"
                f"• /myinfo - Check your information\n"
                f"• /list - List team members\n"
                f"• /status [phone] - Check player status\n\n"
                f"You can also ask me questions in natural language!"
            )
            await update.message.reply_text(fallback_help, parse_mode='Markdown')

    async def _handle_register_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /register command using agentic design with CrewAI agents."""
        try:
            from enums import ChatType
            from features.system_infrastructure.domain.services.permission_service import (
                get_permission_service, PermissionContext
            )
            
            # Determine chat type and create context
            chat_id = str(update.effective_chat.id)
            user_id = str(update.effective_user.id)
            username = update.effective_user.username or update.effective_user.first_name
            
            if chat_id == self.main_chat_id:
                chat_type = ChatType.MAIN
            elif chat_id == self.leadership_chat_id:
                chat_type = ChatType.LEADERSHIP
            else:
                chat_type = ChatType.PRIVATE
            
            # Create permission context
            permission_context = PermissionContext(
                user_id=user_id,
                team_id=self.team_id,
                chat_id=chat_id,
                chat_type=chat_type,
                username=username
            )
            
            # Check if user is already registered
            permission_service = get_permission_service()
            is_registered = await permission_service.is_user_registered(permission_context)
            
            if is_registered:
                response = (
                    f"👋 *{update.effective_user.first_name}*, you are already registered!\n\n"
                    f"📋 *Your Options:*\n"
                    f"• Use /myinfo to check your details\n"
                    f"• Use /list to see the team\n"
                    f"• Use /status [phone] to check your status\n\n"
                    f"💡 *Need to update your info?*\n"
                    f"Contact the team leadership for any changes."
                )
                await update.message.reply_text(response, parse_mode='Markdown')
                logger.info(f"✅ Already registered user {user_id} attempted registration")
                return
            
            # AGENTIC APPROACH: Use CrewAI agents for registration
            # Get the CrewAI system from the bot manager
            crewai_system = self._get_crewai_system()
            if not crewai_system:
                # Fallback to direct handling if agents unavailable
                response = await self._handle_registration_fallback(update, permission_context, chat_type)
                await update.message.reply_text(response, parse_mode='Markdown')
                return
            
            # Create execution context for agents
            execution_context = {
                'team_id': self.team_id,
                'user_id': user_id,
                'chat_id': chat_id,
                'chat_type': chat_type.value,
                'username': username,
                'message_text': '/register',
                'command': 'register'
            }
            
            # Use ONBOARDING_AGENT for registration
            onboarding_agent = crewai_system.agents.get('onboarding_agent')
            if onboarding_agent:
                # Create registration task based on chat type
                if chat_type == ChatType.MAIN:
                    task = "Handle player registration in main chat. Guide user through providing full player details including name, phone, position, date of birth, emergency contact, and next of kin. Validate all inputs and provide helpful guidance."
                elif chat_type == ChatType.LEADERSHIP:
                    task = "Handle team member registration in leadership chat. Guide user through providing team member details including name, phone, and role. Make additional fields optional."
                else:
                    task = "Provide registration guidance for private chat. Explain the difference between player and team member registration and direct user to appropriate chat."
                
                # Execute with agent
                response = await onboarding_agent.execute(task, execution_context)
                await update.message.reply_text(response, parse_mode='Markdown')
                logger.info(f"✅ Agentic registration completed for user {user_id}")
            else:
                # Fallback if onboarding agent not available
                response = await self._handle_registration_fallback(update, permission_context, chat_type)
                await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error in agentic registration: {e}")
            # Use COMMAND_FALLBACK_AGENT for error handling
            try:
                crewai_system = self._get_crewai_system()
                if crewai_system:
                    fallback_agent = crewai_system.agents.get('command_fallback_agent')
                    if fallback_agent:
                        error_context = {
                            'team_id': self.team_id,
                            'user_id': str(update.effective_user.id),
                            'chat_id': str(update.effective_chat.id),
                            'error': str(e),
                            'command': 'register'
                        }
                        error_response = await fallback_agent.execute(
                            "Handle registration command error. Provide helpful error message and guidance to user.",
                            error_context
                        )
                        await update.message.reply_text(error_response, parse_mode='Markdown')
                        return
            except:
                pass
            
            # Final fallback
            await update.message.reply_text(
                "❌ Sorry, I encountered an error processing your registration.\n"
                "Please try again or contact the team leadership for assistance."
            )
    
    def _get_crewai_system(self):
        """Get the CrewAI system from the bot manager."""
        try:
            # This would need to be passed from the MultiBotManager
            # For now, return None to use fallback
            return None
        except Exception as e:
            logger.error(f"Error getting CrewAI system: {e}")
            return None
    
    async def _handle_registration_fallback(self, update: Update, context: PermissionContext, chat_type: ChatType) -> str:
        """Fallback registration handling when agents are unavailable."""
        try:
            if chat_type == ChatType.MAIN:
                return await self._handle_player_registration(update, context)
            elif chat_type == ChatType.LEADERSHIP:
                return await self._handle_team_member_registration(update, context)
            else:
                return await self._handle_private_registration(update, context)
        except Exception as e:
            logger.error(f"Error in registration fallback: {e}")
            return "❌ Error setting up registration. Please try again."
    
    async def _handle_player_registration(self, update: Update, context: PermissionContext) -> str:
        """Handle player registration in main chat."""
        try:
            # Check if this is the first user (should be in leadership chat)
            permission_service = get_permission_service()
            is_first_user = await permission_service.is_first_user(self.team_id)
            
            if is_first_user:
                return (
                    f"🎯 *First User Registration*\n\n"
                    f"Welcome! You appear to be the first user in this system.\n"
                    f"You'll be set up as the team administrator.\n\n"
                    f"📝 *Please provide your details:*\n"
                    f"• **Full Name**: (e.g., John Smith)\n"
                    f"• **Phone Number**: (e.g., +447123456789)\n"
                    f"• **Position**: (e.g., Forward, Midfielder, etc.)\n"
                    f"• **Date of Birth**: (e.g., 1990-01-15)\n"
                    f"• **Emergency Contact**: (e.g., +447123456789)\n\n"
                    f"💡 *Send all details in one message* like this:\n"
                    f"`John Smith, +447123456789, Forward, 1990-01-15, +447123456789`"
                )
            
            # Regular player registration
            return (
                f"🎯 *Player Registration*\n\n"
                f"Welcome to the team! Let's get you registered as a player.\n\n"
                f"📝 *Please provide your details:*\n"
                f"• **Full Name**: (e.g., John Smith)\n"
                f"• **Phone Number**: (e.g., +447123456789)\n"
                f"• **Position**: (e.g., Forward, Midfielder, Defender, Goalkeeper)\n"
                f"• **Date of Birth**: (e.g., 1990-01-15)\n"
                f"• **Emergency Contact**: (e.g., +447123456789)\n"
                f"• **Next of Kin**: (e.g., Jane Smith - Wife)\n\n"
                f"💡 *Send all details in one message* like this:\n"
                f"`John Smith, +447123456789, Forward, 1990-01-15, +447123456789, Jane Smith - Wife`\n\n"
                f"⚠️ *Note*: You must be added by team leadership first. If you haven't been invited, please contact the team admin."
            )
            
        except Exception as e:
            logger.error(f"Error in player registration: {e}")
            return "❌ Error setting up player registration. Please try again."
    
    async def _handle_team_member_registration(self, update: Update, context: PermissionContext) -> str:
        """Handle team member registration in leadership chat."""
        try:
            return (
                f"👔 *Team Member Registration*\n\n"
                f"Welcome to the leadership team! Let's register you as a team member.\n\n"
                f"📝 *Please provide your details:*\n"
                f"• **Full Name**: (e.g., John Smith)\n"
                f"• **Phone Number**: (e.g., +447123456789)\n"
                f"• **Role**: (e.g., Coach, Manager, Volunteer, Assistant)\n\n"
                f"💡 *Send all details in one message* like this:\n"
                f"`John Smith, +447123456789, Coach`\n\n"
                f"✅ *Optional Information* (add if you want):\n"
                f"• **Email**: (e.g., john@example.com)\n"
                f"• **Experience**: (e.g., 5 years coaching)\n"
                f"• **Notes**: (e.g., FA qualified coach)"
            )
            
        except Exception as e:
            logger.error(f"Error in team member registration: {e}")
            return "❌ Error setting up team member registration. Please try again."
    
    async def _handle_private_registration(self, update: Update, context: PermissionContext) -> str:
        """Handle registration in private chat."""
        try:
            return (
                f"🤖 *Registration Guidance*\n\n"
                f"Hi {update.effective_user.first_name}! I can help you register.\n\n"
                f"📋 *Choose your registration type:*\n\n"
                f"🎯 *Player Registration* (Main Chat):\n"
                f"• Join the main team chat\n"
                f"• Use /register for full player onboarding\n"
                f"• Requires team leadership approval\n\n"
                f"👔 *Team Member Registration* (Leadership Chat):\n"
                f"• Join the leadership chat\n"
                f"• Use /register for team member setup\n"
                f"• For coaches, managers, volunteers\n\n"
                f"💡 *Need help?*\n"
                f"Contact the team leadership to be added to the appropriate chat."
            )
            
        except Exception as e:
            logger.error(f"Error in private registration: {e}")
            return "❌ Error providing registration guidance. Please contact team leadership."

    async def _start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Fallback start handler."""
        await update.message.reply_text("Hello! The bot is running.")

    async def start_polling(self) -> None:
        logger.info("Starting Telegram bot polling...")
        self._running = True
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        logger.info("Telegram bot polling started.")

    async def send_message(self, chat_id: Union[int, str], text: str, **kwargs):
        logger.info(f"Sending message to chat_id={chat_id}: {text}")
        await self.app.bot.send_message(chat_id=chat_id, text=text, **kwargs)

    async def stop(self) -> None:
        logger.info("Stopping Telegram bot...")
        self._running = False
        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()
        logger.info("Telegram bot stopped.") 