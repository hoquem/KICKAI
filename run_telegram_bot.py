#!/usr/bin/env python3
"""
Telegram Bot Runner for KICKAI
Handles incoming Telegram messages and processes commands using LLM-based parsing
"""

# --- MONKEY-PATCH MUST BE FIRST - before any other imports ---
import httpx

# --- Monkey-patch to remove 'proxy' and 'proxies' kwargs from httpx.Client/AsyncClient ---
_original_client_init = httpx.Client.__init__
def _patched_client_init(self, *args, **kwargs):
    kwargs.pop("proxy", None)
    kwargs.pop("proxies", None)
    _original_client_init(self, *args, **kwargs)
httpx.Client.__init__ = _patched_client_init

_original_async_client_init = httpx.AsyncClient.__init__
def _patched_async_client_init(self, *args, **kwargs):
    kwargs.pop("proxy", None)
    kwargs.pop("proxies", None)
    _original_async_client_init(self, *args, **kwargs)
httpx.AsyncClient.__init__ = _patched_async_client_init

# --- Now safe to import other modules ---
import os
import logging
import sys
from dotenv import load_dotenv
from telegram.ext import Application
from src.services.bot_status_service import send_startup_messages, send_shutdown_messages
import signal

# Add src directory to Python path for Railway deployment
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if os.path.exists(src_dir):
    sys.path.insert(0, src_dir)

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_bot_token():
    """Get bot token based on environment.
    
    - Local Development: Uses environment variables directly
    - Production: Uses Firestore database
    """
    try:
        logger.info("🔍 Starting bot token retrieval...")
        
        # Check if we're in local development mode
        environment = os.getenv("ENVIRONMENT", "development")
        
        if environment == "development":
            # For local development, use environment variables directly
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            if not bot_token:
                logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
                logger.error("💡 For local development, create a test bot with @BotFather and set TELEGRAM_BOT_TOKEN in your .env file")
                return None
            
            logger.info("✅ Using bot token from environment variables (local development)")
            logger.info(f"   Bot Token: {bot_token[:10]}...")
            return bot_token
        
        # For production, use the existing Firestore-based configuration
        logger.info("🔧 Using Firestore-based bot configuration (production)")
        
        # Validate required environment variables for production
        required_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_USERNAME", "TELEGRAM_MAIN_CHAT_ID", "TELEGRAM_LEADERSHIP_CHAT_ID"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            error_msg = f"❌ CRITICAL ERROR: Missing required environment variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            logger.error("The bot cannot function without these environment variables.")
            logger.error("Please set them in your environment or .env file.")
            raise ValueError(error_msg)
        
        # Import the bot configuration manager
        logger.info("📦 Importing bot configuration manager...")
        try:
            from src.core.bot_config_manager import get_bot_config_manager
            logger.info("✅ Imported bot configuration manager")
        except ImportError as import_error:
            logger.error(f"❌ Failed to import bot configuration manager: {import_error}")
            raise
        
        # Get the bot configuration manager
        logger.info("🔧 Getting bot configuration manager...")
        try:
            manager = get_bot_config_manager()
            logger.info(f"✅ Bot configuration manager initialized for environment: {manager.environment}")
        except Exception as manager_error:
            logger.error(f"❌ Failed to get bot configuration manager: {manager_error}")
            raise
        
        # Load configuration
        logger.info("📋 Loading bot configuration...")
        try:
            config = manager.load_configuration()
            logger.info(f"✅ Configuration loaded for environment: {config.environment}")
            logger.info(f"📊 Available teams: {list(config.teams.keys())}")
        except Exception as config_error:
            logger.error(f"❌ Failed to load configuration: {config_error}")
            raise
        
        # Get the default team or first available team
        team_id = config.default_team
        if not team_id and config.teams:
            team_id = list(config.teams.keys())[0]
            logger.info(f"📋 No default team set, using first available team: {team_id}")
        
        if not team_id:
            logger.error("❌ No teams found in configuration")
            return None
        
        # Get the bot configuration for the team
        logger.info(f"🔍 Getting bot for team: {team_id}")
        try:
            bot_config = manager.get_bot_config(team_id)
            if not bot_config:
                logger.error(f"❌ No bot found for team: {team_id}")
                return None
            
            bot_token = bot_config.token
            if not bot_token:
                logger.error(f"❌ Bot token is empty for team: {team_id}")
                return None
            
            logger.info(f"✅ Bot token retrieved successfully: {bot_token[:10]}...")
            logger.info(f"   Team: {team_id}")
            logger.info(f"   Bot Username: {bot_config.username}")
            logger.info(f"   Main Chat ID: {bot_config.main_chat_id}")
            logger.info(f"   Leadership Chat ID: {bot_config.leadership_chat_id}")
            return bot_token
            
        except Exception as bot_error:
            logger.error(f"❌ Failed to get bot configuration for team {team_id}: {bot_error}")
            raise
            
    except Exception as e:
        logger.error(f"❌ Error getting bot token: {e}")
        return None

def test_bot_connection(bot_token):
    """Test bot connection and get bot info."""
    import requests
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        bot_info = response.json()
        
        if bot_info.get('ok'):
            bot = bot_info['result']
            logger.info(f"✅ Bot connected successfully!")
            logger.info(f"   Name: {bot.get('first_name')}")
            logger.info(f"   Username: @{bot.get('username')}")
            logger.info(f"   ID: {bot.get('id')}")
            return True
        else:
            logger.error(f"❌ Bot connection failed: {bot_info}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing bot connection: {e}")
        return False

def main():
    """Main function to run the bot with LLM-based command parsing."""
    print("🏆 KICKAI Telegram Bot Runner (Firebase + LLM Parsing)")
    print("=" * 50)
    
    # Note: Health server is handled by railway_main.py, not needed here
    logger.info("✅ Health server managed by railway_main.py")
    
    try:
        # Get bot token based on environment
        bot_token = get_bot_token()
        if not bot_token:
            print("❌ Bot token not found. Exiting.")
            return
        
        # Test connection
        print("\n🔍 Testing bot connection...")
        if not test_bot_connection(bot_token):
            print("❌ Bot connection failed. Check your bot token.")
            return
        
        # Get team_id for status messages
        from src.core.bot_config_manager import get_bot_config_manager
        manager = get_bot_config_manager()
        config = manager.load_configuration()
        team_id = config.default_team or (list(config.teams.keys())[0] if config.teams else None)
        
        # Send startup message
        if bot_token and team_id:
            send_startup_messages(bot_token, team_id)
        
        # Set up python-telegram-bot Application
        print("\n🚀 Setting up LLM-based bot...")
        app = Application.builder().token(bot_token).build()
        
        # Register unified message handler (replaces all complex routing)
        try:
            from src.telegram.unified_message_handler import register_unified_handler
            if team_id:
                register_unified_handler(app, team_id)
            else:
                register_unified_handler(app)  # Use default team ID
            logger.info("✅ Unified message handler registered")
        except Exception as e:
            logger.error(f"❌ Failed to register unified message handler: {e}")
            print("❌ Failed to register unified message handler. Registering fallback system error handler.")
            from src.telegram.telegram_command_handler import fallback_system_error_handler
            from telegram.ext import MessageHandler, filters
            app.add_handler(MessageHandler(filters.ALL, fallback_system_error_handler))
            logger.info("✅ Fallback system error handler registered for all messages")
        
        print("✅ Bot is running with Firebase + 8-agent CrewAI system! Send messages to your Telegram groups to test.")
        print("🔥 Firebase Firestore database enabled")
        print("🤖 Agent-based natural language processing enabled:")
        print("   • Message Processing Specialist - Primary interface")
        print("   • Team Manager - Strategic coordination")
        print("   • Player Coordinator - Operational management")
        print("   • Match Analyst - Tactical analysis")
        print("   • Communication Specialist - Broadcast management")
        print("   • Finance Manager - Financial management")
        print("   • Squad Selection Specialist - Squad selection")
        print("   • Analytics Specialist - Performance analytics")
        print("🔄 Background tasks and reminders enabled:")
        print("   • Automated onboarding reminders")
        print("   • FA registration checks")
        print("   • Daily status reports")
        print("   • Reminder cleanup service")
        print("📋 New commands available:")
        print("   • /background_tasks - Check background task status")
        print("   • /remind [player_id] - Send manual reminder")
        print("   • /help - View all available commands")
        print("💡 Try: \"Create a match against Arsenal on July 1st at 2pm\"")
        print("💡 Try: \"Plan our next match including squad selection\"")
        print("💡 Try: \"Analyze our team performance and suggest improvements\"")
        print("💡 Try: \"/background_tasks\" to check system status")
        print("💡 Press Ctrl+C to stop the bot.")

        def handle_shutdown(signum, frame):
            logger.info(f"Received signal {signum}, sending shutdown messages...")
            if bot_token and team_id:
                send_shutdown_messages(bot_token, team_id)
            sys.exit(0)

        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)
        
        # Run the bot with polling
        app.run_polling()
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Make sure bot token is available in the environment or configuration")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.error(f"Bot error: {e}", exc_info=True)
    finally:
        # On normal exit, send shutdown message
        try:
            bot_token = get_bot_token()
            from src.core.bot_config_manager import get_bot_config_manager
            manager = get_bot_config_manager()
            config = manager.load_configuration()
            team_id = config.default_team or (list(config.teams.keys())[0] if config.teams else None)
            if bot_token and team_id:
                send_shutdown_messages(bot_token, team_id)
        except Exception as e:
            logger.error(f"❌ Error sending shutdown message on exit: {e}")

if __name__ == "__main__":
    main() 