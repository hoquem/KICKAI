#!/usr/bin/env python3
"""
KICKAI Bot Startup Script - Local Development

A clean, robust bot startup script for local development with console-only logging.
File logging is handled through redirection in the startup script.
"""

import asyncio
import os
import signal
import sys
import time
from pathlib import Path
from typing import Optional

# Enable nested event loops for environments that already have an event loop running
import nest_asyncio
nest_asyncio.apply()

from kickai.core.settings import initialize_settings, get_settings
from kickai.database.firebase_client import initialize_firebase_client
from kickai.features.team_administration.domain.services.multi_bot_manager import MultiBotManager
from kickai.core.dependency_container import get_service, get_singleton, ensure_container_initialized
from kickai.features.team_administration.domain.interfaces.team_service_interface import ITeamService
from kickai.features.player_registration.domain.interfaces.player_service_interface import IPlayerService
from kickai.core.startup_validator import StartupValidator
from kickai.core.logging_config import logger

# Global state
multi_bot_manager: Optional[MultiBotManager] = None
shutdown_event = asyncio.Event()


def setup_logging():
    """Configure logging for local development - console only."""
    # Loguru is already configured in core.logging_config to log to console only
    logger.info("📝 Logging configured for local development")
    logger.info("📄 Console output only - file logging handled by redirection")
    logger.info("🔄 Local development mode enabled")


def cleanup_existing_bots():
    """Kill existing bot processes before starting."""
    try:
        import subprocess
        logger.info("🧹 Cleaning up existing bot processes...")
        
        # Kill any existing bot processes
        subprocess.run(["pkill", "-f", "run_bot_local.py"], capture_output=True)
        subprocess.run(["pkill", "-f", "python.*bot"], capture_output=True)
        
        # Wait for processes to terminate
        time.sleep(2)
        logger.info("✅ Bot cleanup completed")
        
    except Exception as e:
        logger.warning(f"⚠️ Could not cleanup existing bots: {e}")

def setup_environment():
    """Set up the environment and load configuration."""
    try:
        # Clean up existing bot processes first
        cleanup_existing_bots()
        
        # Load environment variables from .env file
        from dotenv import load_dotenv
        load_dotenv()
        
        # Initialize settings
        initialize_settings()
        config = get_settings()
        
        # Validate required fields (only Firebase and AI config, not bot tokens)
        errors = config.validate_required_fields()
        if errors:
            logger.error("❌ Configuration errors:")
            for error in errors:
                logger.error(f"   - {error}")
            raise ValueError("Configuration validation failed")
        
        # Configure logging
        setup_logging()
        logger.info("✅ Configuration loaded successfully and logging configured")
        
        # Set up CrewAI logging to redirect to loguru
        from kickai.utils.crewai_logging import setup_crewai_logging
        setup_crewai_logging("DEBUG")  # Use DEBUG level for local development
        
        # Initialize Firebase
        initialize_firebase_client(config)
        logger.info("✅ Firebase client initialized")
        
        # Ensure dependency container is initialized with Firebase client
        ensure_container_initialized()
        logger.info("✅ Dependency container initialized with Firebase client")
        
        return config
        
    except Exception as e:
        logger.critical(f"❌ Failed to setup environment: {e}", exc_info=True)
        raise


async def run_system_validation():
    """Run comprehensive system validation before starting bots."""
    try:
        logger.info("🔍 Running system validation...")
        
        # Use the centralized startup validation function
        from kickai.core.startup_validation import run_startup_validation
        
        report = await run_startup_validation(team_id="KTI")
        
        # Check if system is healthy
        if not report.is_healthy():
            logger.warning("⚠️ System validation completed with warnings")
            logger.warning("Bot will start but some features may not work correctly")
        else:
            logger.info("✅ System validation completed successfully")
        
        return report.is_healthy()
        
    except Exception as e:
        logger.error(f"❌ System validation failed: {e}", exc_info=True)
        logger.warning("⚠️ Continuing with bot startup despite validation errors")
        return False


async def create_multi_bot_manager():
    """Create and configure the multi-bot manager."""
    try:
        logger.info("🤖 Creating multi-bot manager...")
        
        # Get the multi-bot manager service
        multi_bot_manager = get_service(MultiBotManager)
        
        # Initialize the manager
        await multi_bot_manager.initialize()
        logger.info("✅ Multi-bot manager created and initialized")
        
        return multi_bot_manager
        
    except Exception as e:
        logger.error(f"❌ Failed to create multi-bot manager: {e}", exc_info=True)
        raise


def flush_and_close_loggers():
    """Flush and close all loggers."""
    try:
        logger.info("🔄 Flushing and closing loggers...")
        # Loguru handles this automatically
        logger.info("✅ Loggers closed successfully")
    except Exception as e:
        print(f"❌ Error closing loggers: {e}")


async def main():
    """Main bot startup function."""
    global multi_bot_manager
    
    def _signal_handler():
        """Handle shutdown signals."""
        logger.info("🛑 Received shutdown signal, initiating graceful shutdown...")
        shutdown_event.set()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, lambda s, f: _signal_handler())
    signal.signal(signal.SIGTERM, lambda s, f: _signal_handler())
    
    try:
        logger.info("🚀 Starting KICKAI Bot - Local Development")
        logger.info("=" * 60)
        
        # Set up environment
        config = setup_environment()
        
        # Run system validation
        validation_success = await run_system_validation()
        
        # Only proceed if validation is successful
        if not validation_success:
            logger.critical("❌ Critical validation failures detected. Bot startup aborted.")
            logger.critical("Please fix the validation issues before starting the bot.")
            return
        
        # Create multi-bot manager
        multi_bot_manager = await create_multi_bot_manager()
        
        # Start all bots and begin polling
        logger.info("🚀 Starting all Telegram bots...")
        await multi_bot_manager.start_all_bots()
        
        # Send startup messages to all chats
        logger.info("📢 Sending startup messages...")
        await multi_bot_manager.send_startup_messages()
        
        logger.info("✅ Bot startup completed successfully")
        logger.info("🤖 Bot is now running and ready to receive messages")
        logger.info("📝 Check console output for detailed logs")
        logger.info("🛑 Press Ctrl+C to stop the bot")
        logger.info("=" * 60)
        
        # Keep the bot running until shutdown signal
        while not shutdown_event.is_set():
            await asyncio.sleep(1)
        
        logger.info("🛑 Shutdown signal received, stopping bot...")
        
    except KeyboardInterrupt:
        logger.info("🛑 Keyboard interrupt received, stopping bot...")
    except Exception as e:
        logger.critical(f"❌ Critical error during bot startup: {e}", exc_info=True)
        raise
    finally:
        # Cleanup
        if multi_bot_manager:
            try:
                await multi_bot_manager.shutdown()
                logger.info("✅ Multi-bot manager shutdown completed")
            except Exception as e:
                logger.error(f"❌ Error during multi-bot manager shutdown: {e}")
        
        flush_and_close_loggers()
        logger.info("👋 Bot shutdown completed")


def main_sync():
    """Synchronous wrapper for the main function."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main_sync() 