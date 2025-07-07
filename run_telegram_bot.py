#!/usr/bin/env python3
"""
KICKAI Telegram Bot Runner

This script starts the KICKAI system with Telegram bot integration.
It initializes all components and starts the bot to handle messages.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Enable nested event loops for environments that already have an event loop running
import nest_asyncio
nest_asyncio.apply()

from telegram.ext import Application, CommandHandler
from src.core.improved_config_system import initialize_improved_config, get_improved_config
from src.database.firebase_client import initialize_firebase_client
from src.telegram.unified_message_handler import register_unified_handler
from src.services.player_service import initialize_player_service
from src.services.team_service import initialize_team_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('kickai_bot.log')
    ]
)
logger = logging.getLogger(__name__)


def check_network_connectivity():
    """Check basic network connectivity."""
    try:
        import requests
        # Test connection to Telegram API
        response = requests.get("https://api.telegram.org", timeout=10)
        if response.status_code == 200:
            logger.info("✅ Network connectivity: OK")
            return True
        else:
            logger.warning(f"⚠️ Network connectivity: HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.warning(f"⚠️ Network connectivity: {e}")
        return False

def setup_environment():
    """Set up the environment and load configuration."""
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check network connectivity
        check_network_connectivity()
        
        # Initialize configuration manager and get Configuration object
        initialize_improved_config()
        config = get_improved_config().configuration
        logger.info("✅ Configuration loaded successfully")
        
        # Initialize Firebase with database config
        initialize_firebase_client(config.database)
        logger.info("✅ Firebase client initialized")
        
        # Initialize services
        initialize_player_service()
        initialize_team_service()
        logger.info("✅ Services initialized")
        
        return config
        
    except Exception as e:
        logger.error(f"❌ Failed to setup environment: {e}")
        raise


def start_bot(config):
    """Start the Telegram bot."""
    try:
        # Get bot token from config
        bot_token = config.telegram.bot_token
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        logger.info(f"🤖 Starting KICKAI Telegram Bot...")
        logger.info(f"   Bot Token: {bot_token[:10]}...")
        
        # Create application
        application = Application.builder().token(bot_token).build()
        
        # Register the unified message handler
        team_id = "0854829d-445c-4138-9fd3-4db562ea46ee"  # Default team ID
        register_unified_handler(application, team_id)
        
        # Add basic command handlers
        from src.telegram.unified_command_system import get_command_registry
        
        command_registry = get_command_registry()
        
        # Register all commands
        for command in command_registry.get_all_commands():
            application.add_handler(
                CommandHandler(command.name[1:], command.execute)  # Remove / from command name
            )
        
        logger.info("✅ Bot handlers registered successfully")
        
        # Start the bot
        logger.info("🚀 Starting bot polling...")
        
        # Use run_polling with network resilience settings
        logger.info("📡 Starting resilient polling with network recovery...")
        
        # TODO: To enable startup messages, uncomment the following lines:
        # async def send_startup_messages():
        #     try:
        #         main_chat_id = os.getenv("TELEGRAM_MAIN_CHAT_ID")
        #         leadership_chat_id = os.getenv("TELEGRAM_LEADERSHIP_CHAT_ID")
        #         
        #         message = "🤖 **KICKAI Bot is now online!**\n\n✅ System initialized successfully\n✅ All services are running\n✅ Ready to handle commands"
        #         
        #         if main_chat_id:
        #             await application.bot.send_message(chat_id=main_chat_id, text=message, parse_mode='Markdown')
        #         if leadership_chat_id:
        #             await application.bot.send_message(chat_id=leadership_chat_id, text=message, parse_mode='Markdown')
        #     except Exception as e:
        #         logger.warning(f"Failed to send startup messages: {e}")
        # 
        # # Send startup messages after a short delay
        # import asyncio
        # asyncio.create_task(send_startup_messages())
        
        application.run_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True,
            close_loop=False
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        raise


def main():
    """Main entry point."""
    try:
        logger.info("🎯 KICKAI Telegram Bot Starting...")
        
        # Setup environment
        config = setup_environment()
        
        # Start the bot
        start_bot(config)
        
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if required environment variables are set
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "GOOGLE_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    # Accept either FIREBASE_CREDENTIALS_JSON or FIREBASE_CREDENTIALS_FILE
    if not (os.getenv("FIREBASE_CREDENTIALS_JSON") or os.getenv("FIREBASE_CREDENTIALS_FILE")):
        missing_vars.append("FIREBASE_CREDENTIALS_JSON or FIREBASE_CREDENTIALS_FILE")
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please set these variables in your .env file or environment.")
        print("📖 See README.md for setup instructions.")
        sys.exit(1)
    
    # Run the bot
    main() 