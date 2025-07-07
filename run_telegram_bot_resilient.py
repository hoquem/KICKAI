#!/usr/bin/env python3
"""
Resilient KICKAI Telegram Bot Runner

This script starts the KICKAI system with enhanced network resilience
for slow or intermittent network connections.

IMPORTANT: This script will exit immediately on any fatal error.
Use an external process manager (systemd, supervisor, pm2, or a shell script)
to restart the bot if it exits unexpectedly.
"""

import asyncio
import logging
import os
import sys
import time
import signal
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
        logging.FileHandler('kickai_bot_resilient.log')
    ]
)
logger = logging.getLogger(__name__)

# Global state
application = None
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    logger.info(f"🛑 Received signal {signum}, initiating graceful shutdown...")
    shutdown_requested = True


async def check_network_connectivity():
    """Check basic network connectivity with retry."""
    for attempt in range(3):
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.telegram.org", timeout=30) as response:
                    if response.status == 200:
                        logger.info("✅ Network connectivity: OK")
                        return True
                    else:
                        logger.warning(f"⚠️ Network connectivity: HTTP {response.status}")
        except Exception as e:
            logger.warning(f"⚠️ Network connectivity attempt {attempt + 1}: {e}")
            if attempt < 2:
                await asyncio.sleep(5)
    return False


async def setup_environment():
    """Set up the environment and load configuration."""
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check network connectivity
        await check_network_connectivity()
        
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
        sys.exit(1)


async def create_application(config):
    """Create and configure the Telegram application."""
    global application
    
    try:
        # Get bot token from config
        bot_token = config.telegram.bot_token
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        logger.info(f"🤖 Creating KICKAI Telegram Bot (Resilient Mode)...")
        logger.info(f"   Bot Token: {bot_token[:10]}...")
        
        # Create application with enhanced timeout settings
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
        
        return application
        
    except Exception as e:
        logger.error(f"❌ Failed to create application: {e}")
        sys.exit(1)


async def send_startup_messages(app):
    """Send startup messages to main and leadership chats."""
    try:
        # Get bot info
        bot_info = await app.bot.get_me()
        bot_name = bot_info.first_name
        
        # Get chat IDs from environment
        main_chat_id = os.getenv("TELEGRAM_MAIN_CHAT_ID")
        leadership_chat_id = os.getenv("TELEGRAM_LEADERSHIP_CHAT_ID")
        
        startup_message = f"🚀 <b>{bot_name} is now online!</b>\n\n✅ Bot started successfully\n📡 Ready to receive messages\n🕐 {time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Send to main chat if configured
        if main_chat_id:
            try:
                await app.bot.send_message(
                    chat_id=main_chat_id,
                    text=startup_message,
                    parse_mode='HTML'
                )
                logger.info(f"✅ Startup message sent to main chat")
            except Exception as e:
                logger.warning(f"⚠️ Failed to send startup message to main chat: {e}")
        
        # Send to leadership chat if configured
        if leadership_chat_id:
            try:
                await app.bot.send_message(
                    chat_id=leadership_chat_id,
                    text=startup_message,
                    parse_mode='HTML'
                )
                logger.info(f"✅ Startup message sent to leadership chat")
            except Exception as e:
                logger.warning(f"⚠️ Failed to send startup message to leadership chat: {e}")
                
    except Exception as e:
        logger.warning(f"⚠️ Failed to send startup messages: {e}")


async def main_async():
    """Main async entry point with enhanced error handling."""
    global application, shutdown_requested
    
    try:
        if shutdown_requested:
            logger.info("🛑 Shutdown requested, stopping...")
            sys.exit(0)
        
        logger.info(f"🎯 KICKAI Telegram Bot Starting...")
        
        # Setup environment
        config = await setup_environment()
        
        # Create application
        app = await create_application(config)
        
        # Initialize the application
        await app.initialize()
        logger.info("✅ Application initialized")
        
        # Send startup messages
        await send_startup_messages(app)
        
        # Start the application
        await app.start()
        logger.info("✅ Application started")
        
        # Start polling with proper error handling
        logger.info("📡 Starting ultra-resilient polling...")
        
        # Use the application's run_polling method instead of manual polling
        await app.run_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True,
            close_loop=False
        )
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
    finally:
        # Ensure proper cleanup
        if application:
            try:
                logger.info("🧹 Cleaning up application...")
                await application.stop()
                await application.shutdown()
                logger.info("✅ Application cleaned up")
            except Exception as e:
                logger.warning(f"⚠️ Error during cleanup: {e}")


def main():
    """Main entry point."""
    try:
        # Run the async main function
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
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