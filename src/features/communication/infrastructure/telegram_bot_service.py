import os
from typing import Union
from loguru import logger
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from features.communication.domain.interfaces.telegram_bot_service_interface import TelegramBotServiceInterface

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
        """Handle the /help command."""
        try:
            from bot_telegram.command_parser import get_improved_parser
            
            parser = get_improved_parser()
            help_text = parser.get_help_text()
            
            await update.message.reply_text(help_text, parse_mode='Markdown')
            logger.info(f"✅ Help command handled for user {update.effective_user.id}")
            
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