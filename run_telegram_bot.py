#!/usr/bin/env python3
"""
KICKAI Telegram Bot Runner

This script starts the KICKAI system with Telegram bot integration.
It initializes all components and starts the bot to handle messages.
"""

import asyncio
import signal
import logging
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Enable nested event loops for environments that already have an event loop running
import nest_asyncio
nest_asyncio.apply()

from core.constants import BOT_VERSION, FIRESTORE_COLLECTION_PREFIX
from core.settings import get_settings, initialize_settings
from database.firebase_client import initialize_firebase_client
from services.player_service import get_player_service
from services.team_service import get_team_service
from bot_telegram.unified_message_handler import UnifiedMessageHandler, register_unified_handler
from bot_telegram.unified_command_system import get_command_registry
from telegram.ext import ApplicationBuilder, Application, CommandHandler

# Configure logging
logger = logging.getLogger(__name__)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't interfere with Ctrl+C
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Unhandled exception caught by sys.excepthook:", exc_info=(exc_type, exc_value, exc_traceback))
    # Force flush all handlers
    for handler in logger.handlers:
        handler.flush()
    sys.exit(1) # Exit with an error code

sys.excepthook = handle_exception

# Ensure logs are flushed immediately
for handler in logger.handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.flush = sys.stdout.flush # For stdout
    elif isinstance(handler, logging.FileHandler):
        handler.flush() # For files


VERSION = BOT_VERSION


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
        initialize_settings()
        config = get_settings()
        
        # Configure logging with the path from settings
        from core.logging_config import configure_logging
        log_file_path = config.log_file_path if config.log_file_path else "logs/kickai.log"
        configure_logging(
            log_level=config.log_level,
            log_format=config.log_format,
            log_file=log_file_path,
            max_file_size=config.log_max_file_size,
            backup_count=config.log_backup_count,
            include_context=True # Always include context for structured logging
        )
        logger.info("✅ Configuration loaded successfully and logging configured")
        
        # Initialize Firebase with database config
        initialize_firebase_client(config)
        logger.info("✅ Firebase client initialized")
        
        # Initialize services
        initialize_player_service()
        initialize_team_service()
        
        logger.info("✅ Services initialized")
        
        return config
        
    except Exception as e:
        logger.critical(f"❌ Failed to setup environment: {e}", exc_info=True)
        raise

def initialize_player_service():
    """Initialize the player service."""
    try:
        # This will be initialized when first accessed
        pass
    except Exception as e:
        logger.error(f"❌ Failed to initialize player service: {e}")
        raise

def initialize_team_service():
    """Initialize the team service."""
    try:
        # This will be initialized when first accessed
        pass
    except Exception as e:
        logger.error(f"❌ Failed to initialize team service: {e}")
        raise

# Add global application variable
_application = None

def get_chat_ids():
    main_chat_id = os.getenv("TELEGRAM_MAIN_CHAT_ID")
    leadership_chat_id = os.getenv("TELEGRAM_LEADERSHIP_CHAT_ID")
    chat_ids = []
    if main_chat_id:
        chat_ids.append(main_chat_id)
    if leadership_chat_id and leadership_chat_id != main_chat_id:
        chat_ids.append(leadership_chat_id)
    return chat_ids

async def send_startup_message(application: Application) -> None:
    """Send a startup message to configured chat IDs."""
    import os
    main_chat_id = os.getenv("TELEGRAM_MAIN_CHAT_ID")
    leadership_chat_id = os.getenv("TELEGRAM_LEADERSHIP_CHAT_ID")
    message = f"✅ **KICKAI Bot v{VERSION} started**\n\n🤖 Bot is now online."
    for chat_id, label in [
        (main_chat_id, "main chat"),
        (leadership_chat_id, "leadership chat")
    ]:
        if chat_id:
            try:
                await application.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='Markdown'
                )
                logger.info(f"✅ Startup message sent to {label}: {chat_id}")
            except Exception as e:
                logger.error(f"❌ Failed to send startup message to {label} ({chat_id}): {e}")

async def send_shutdown_message(application: Application) -> None:
    import os
    logger = logging.getLogger(__name__)
    logger.info("🔄 [Shutdown] post_stop callback triggered.")
    main_chat_id = os.getenv("TELEGRAM_MAIN_CHAT_ID")
    leadership_chat_id = os.getenv("TELEGRAM_LEADERSHIP_CHAT_ID")
    message = f"🛑 **KICKAI Bot v{VERSION} is shutting down**\n\n👋 Bot will be offline until restarted"
    for chat_id, label in [
        (main_chat_id, "main chat"),
        (leadership_chat_id, "leadership chat")
    ]:
        if chat_id:
            try:
                await application.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='Markdown'
                )
                logger.info(f"✅ [Shutdown] Shutdown message sent to {label}: {chat_id}")
            except Exception as e:
                logger.error(f"❌ [Shutdown] Failed to send shutdown message to {label} ({chat_id}): {e}")
    logger.info("🔄 [Shutdown] post_stop callback complete.")

async def main():
    try:
        # Load config and initialize application as before
        config = setup_environment()
        
        # Run comprehensive startup validation
        logger.info("🔍 Running comprehensive startup validation...")
        try:
            from core.startup_validator import StartupValidator
            
            # Create and run startup validator
            validator = StartupValidator()
            validation_report = await validator.validate()
            
            # Check if any critical checks failed
            if not validation_report.is_healthy():
                logger.error("❌ Critical startup validation failures detected:")
                for failure in validation_report.critical_failures:
                    logger.error(f"   - {failure}")
                logger.error("🚫 Bot startup aborted due to critical validation failures")
                return
            
            # Log validation summary
            total_checks = len(validation_report.checks)
            passed = len([r for r in validation_report.checks if r.status.value == "PASSED"])
            failed = len([r for r in validation_report.checks if r.status.value == "FAILED"])
            warnings = len([r for r in validation_report.checks if r.status.value == "WARNING"])
            
            logger.info(f"✅ Startup validation complete: {passed}/{total_checks} passed, {failed} failed, {warnings} warnings")
            
            if failed > 0 or warnings > 0:
                logger.warning("⚠️ Some validation checks failed or have warnings:")
                for result in validation_report.checks:
                    if result.status.value in ["FAILED", "WARNING"]:
                        logger.warning(f"   - {result.category.value}:{result.name}: {result.message}")
            
            # Print detailed report
            validator.print_report(validation_report)
            
        except Exception as e:
            logger.error(f"❌ Startup validation failed: {e}")
            logger.error("🚫 Bot startup aborted due to validation error")
            return
        
        application = start_bot(config)  # This should be the function that returns the Application instance
        VERSION = "1.0.0" # Replace with actual version retrieval logic
        chat_ids = get_chat_ids()
        
        # Startup message will be sent automatically by post_init callback
        # --- End application creation logic ---

        # Set up signal handling for graceful shutdown
        shutdown_event = asyncio.Event()
        
        def signal_handler(signum, frame):
            logger.info(f"🛑 Received signal {signum}, initiating graceful shutdown...")
            shutdown_event.set()
        
        import signal
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            logger.info("🤖 Bot is running. Press Ctrl+C to exit.")
            
            # Create polling task
            polling_task = asyncio.create_task(
                application.run_polling(
                    allowed_updates=["message", "callback_query"],
                    drop_pending_updates=True,
                    close_loop=False  # Don't close the loop, let it run naturally
                )
            )
            
            # Wait for either shutdown signal or polling to complete
            await asyncio.wait(
                [polling_task, shutdown_event.wait()],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # If we got here due to shutdown signal, cancel the polling task
            if shutdown_event.is_set():
                logger.info("🛑 Shutdown signal received, stopping bot...")
                polling_task.cancel()
                try:
                    await polling_task
                except asyncio.CancelledError:
                    logger.info("✅ Bot polling stopped")
                
        except asyncio.CancelledError:
            logger.info("🛑 Bot polling cancelled")
        except Exception as e:
            logger.error(f"❌ Error during bot polling: {e}")
        finally:
            logger.info("🔄 Sending shutdown messages...")
            try:
                await send_shutdown_message(application)
            except Exception as e:
                logger.error(f"❌ Error sending shutdown messages: {e}")
            
            logger.info("🔄 Flushing logs and cleaning up...")
            for handler in logging.getLogger().handlers:
                handler.flush()
            logger.info("✅ Shutdown complete. Exiting.")
    except Exception as e:
        logger.critical(f"Unhandled exception in main: {e}", exc_info=True)
        raise

def start_bot(config):
    """Start the Telegram bot."""
    try:
        # Get bot token from config
        bot_token = config.telegram_bot_token
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        logger.info(f"🤖 Starting KICKAI Telegram Bot...")
        logger.info(f"   Bot Token: {bot_token[:10]}...")
        
        # Create application
        application = (
            ApplicationBuilder()
            .token(bot_token)
            .post_init(send_startup_message)
            .post_stop(send_shutdown_message)
            .build()
        )
        
        # Register the unified message handler
        # Team ID will be resolved dynamically for each message
        register_unified_handler(application)
        
        # Add basic command handlers
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
        
        return application
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        raise

# Add this block at the very top after imports
try:
    import psutil
except ImportError:
    print("psutil is required for process management. Please install it with 'pip install psutil'.")
    sys.exit(1)

def kill_other_bot_instances():
    """Kill other running instances of run_telegram_bot.py except this one."""
    current_pid = os.getpid()
    killed = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] == current_pid:
                continue
            cmdline = proc.info.get('cmdline')
            if not cmdline:
                continue
            # Check if this is another run_telegram_bot.py process
            if any('run_telegram_bot.py' in part for part in cmdline):
                proc.kill()
                killed += 1
                logger.info(f"Killed other bot instance with PID {proc.info['pid']}")
        except Exception as e:
            logger.warning(f"Could not check/kill process {proc}: {e}")
    if killed:
        logger.info(f"Killed {killed} other bot instance(s) before starting new one.")
    else:
        logger.info("No other bot instances found.")

# Call this before anything else in main
if __name__ == "__main__":
    kill_other_bot_instances()
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
    print("KICKAI Bot: Starting up...") # Very early print statement
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Exiting.")
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
        sys.exit(1)
    finally:
        # Ensure all logs are flushed before exiting
        for handler in logging.getLogger().handlers:
            handler.flush() 