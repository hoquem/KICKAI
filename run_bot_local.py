#!/usr/bin/env python3
"""
KICKAI Bot Startup Script - Local Development

A clean, robust bot startup script for local development with console-only logging.
File logging is handled through redirection in the startup script.
"""

import asyncio
import signal
import sys
import time
import threading
from typing import Optional

# Enable nested event loops for environments that already have an event loop running
import nest_asyncio

nest_asyncio.apply()

from kickai.core.dependency_container import (
    ensure_container_initialized,
    ensure_container_initialized_async,
    get_service,
    initialize_container,
)
from kickai.core.logging_config import logger
from kickai.core.config import get_settings
from kickai.database.firebase_client import initialize_firebase_client
from kickai.features.team_administration.domain.services.multi_bot_manager import MultiBotManager
from kickai.features.team_administration.domain.services.team_service import TeamService

# Global state
multi_bot_manager: Optional[MultiBotManager] = None
shutdown_event = asyncio.Event()


def setup_global_exception_handlers():
    """Set up global exception handlers to catch unhandled exceptions."""
    
    def handle_thread_exception(args):
        """Handle unhandled exceptions in threads."""
        logger.error(f"❌ Unhandled exception in thread {args.thread}: {args.exc_value}")
        import traceback
        logger.error(f"❌ Thread exception traceback: {traceback.format_exc()}")
        
        # Send a user-friendly error message if possible
        try:
            # This is a fallback - the main error handling should catch most cases
            logger.error("🚨 Critical thread exception - system may be unstable")
        except Exception as e:
            logger.error(f"❌ Failed to handle thread exception: {e}")
    
    def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
        """Handle unhandled exceptions in the main thread."""
        logger.error(f"❌ Unhandled exception: {exc_type.__name__}: {exc_value}")
        import traceback
        logger.error(f"❌ Unhandled exception traceback: {traceback.format_exc()}")
        
        # Don't exit immediately - let the main error handling deal with it
        logger.error("🚨 Unhandled exception detected - attempting graceful recovery")
    
    # Set up thread exception handler
    threading.excepthook = handle_thread_exception
    
    # Set up unhandled exception handler
    sys.excepthook = handle_unhandled_exception
    
    logger.info("✅ Global exception handlers configured")


async def get_team_id_from_firestore() -> str:
    """
    Get the first available team_id from Firestore.
    This ensures we use a real team from the database instead of hardcoded values.
    """
    # Get team service from dependency container
    team_service = get_service(TeamService)
    
    # Get all teams from Firestore
    teams = await team_service.get_all_teams()
    
    if not teams:
        logger.warning("No teams found in Firestore, using fallback team_id")
        return "fallback_team"
    
    # Use the first available team
    team_id = teams[0].id
    logger.info(f"Using team_id from Firestore: {team_id}")
    return team_id


def setup_logging():
    """Configure logging for local development - console only."""
    # Loguru is already configured in core.logging_config to log to console only
    logger.info("📝 Logging configured for local development")
    logger.info("📄 Console output only - file logging handled by redirection")
    logger.info("🔄 Local development mode enabled")


def cleanup_existing_bots():
    """Kill existing bot processes before starting."""
    import subprocess
    logger.info("🧹 Cleaning up existing bot processes...")

    # Kill any existing bot processes
    subprocess.run(["pkill", "-f", "run_bot_local.py"], capture_output=True)
    subprocess.run(["pkill", "-f", "python.*bot"], capture_output=True)

    # Wait for processes to terminate
    time.sleep(2)
    logger.info("✅ Bot cleanup completed")

def setup_environment():
    """Set up the environment and load configuration."""
    # Clean up existing bot processes first
    cleanup_existing_bots()

    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()

    # Note: Container initialization is done later with async team cache
    config = get_settings()

    # Configuration validation is handled automatically by Pydantic
    logger.info("✅ Configuration loaded successfully")

    # Configure logging
    setup_logging()
    logger.info("✅ Configuration loaded successfully and logging configured")

    # Set up CrewAI logging to redirect to loguru
    from kickai.utils.crewai_logging import setup_crewai_logging
    setup_crewai_logging("DEBUG")  # Use DEBUG level for local development
    logger.info("✅ CrewAI logging configured with DEBUG level for verbose output")

    # Also enable CrewAI's internal verbose logging
    import logging
    crewai_logger = logging.getLogger("crewai")
    crewai_logger.setLevel(logging.DEBUG)

    # Initialize Firebase
    initialize_firebase_client(config)
    logger.info("✅ Firebase client initialized")

    # Basic container initialization (async team cache done later)
    ensure_container_initialized()
    logger.info("✅ Basic dependency container initialized")

    return config


async def run_system_validation():
    """Run comprehensive system validation before starting bots."""
    logger.info("🔍 Running comprehensive system validation...")

    # Use our new synchronous comprehensive validation system
    from kickai.core.startup_validation.comprehensive_validator import (
        ComprehensiveStartupValidator,
        validate_system_startup
    )

    # Run the comprehensive validation
    result = validate_system_startup()
    
    # Check if system is healthy
    if not result.success:
        logger.error("❌ System validation failed! Critical issues found:")
        logger.error(f"   • Overall status: FAILED")
        logger.error(f"   • Total checks: {result.total_checks}")
        logger.error(f"   • Passed: {result.passed_checks}")
        logger.error(f"   • Failed: {result.failed_checks}")
        
        if result.critical_failures:
            for failure in result.critical_failures:
                logger.error(f"   • Critical: {failure}")
        
        if result.warnings:
            for warning in result.warnings:
                logger.error(f"   • Warning: {warning}")

        logger.error("🚫 Cannot start bots due to critical validation failures")
        logger.error("🔧 Please run 'python run_comprehensive_validation.py' for detailed diagnostics")
        return False

    if result.warnings:
        logger.warning("⚠️ System validation completed with warnings:")
        for warning in result.warnings:
            logger.warning(f"   • {warning}")
        logger.info("💡 Consider addressing warnings for optimal performance")

    logger.info("✅ System validation passed! All critical components are healthy")
    logger.info(f"📊 Validation Summary: {result.passed_checks}/{result.total_checks} checks passed")
    logger.info("🎉 No stub classes detected - all real implementations are working")
    return True


async def create_multi_bot_manager():
    """Create and configure the multi-bot manager."""
    logger.info("🤖 Creating multi-bot manager...")

    # Get the multi-bot manager service
    multi_bot_manager = get_service(MultiBotManager)

    # Initialize the manager
    await multi_bot_manager.initialize()
    logger.info("✅ Multi-bot manager created and initialized")

    return multi_bot_manager


def flush_and_close_loggers():
    """Flush and close all loggers."""
    logger.info("🔄 Flushing and closing loggers...")
    # Loguru handles this automatically
    logger.info("✅ Loggers closed successfully")


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

        # Set up global exception handlers first
        setup_global_exception_handlers()

        # Set up environment
        config = setup_environment()
        
        # Initialize command registry early to ensure it's available
        logger.info("🔧 Initializing command registry...")
        from kickai.core.command_registry_initializer import initialize_command_registry
        command_registry = initialize_command_registry()
        commands = command_registry.list_all_commands()
        logger.info(f"✅ Command registry initialized with {len(commands)} commands")

        # Run system validation
        validation_success = await run_system_validation()

        # Only proceed if validation is successful
        if not validation_success:
            logger.critical("❌ Critical validation failures detected. Bot startup aborted.")
            logger.critical("Please fix the validation issues before starting the bot.")
            return

        # Initialize container with team config cache for optimal performance
        logger.info("⚡ Initializing team config cache for optimal /addplayer performance...")
        await ensure_container_initialized_async()
        logger.info("✅ Container fully initialized with team config cache")

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
