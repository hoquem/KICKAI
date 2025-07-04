#!/usr/bin/env python3
"""
Railway Main Entry Point for KICKAI

This module serves as the main entry point for Railway deployment.
It starts both the Telegram bot and background tasks in a single process.
"""

import asyncio
import logging
import os
import signal
import sys
from contextlib import asynccontextmanager
from typing import Optional

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if sys.path and src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import required modules
from src.core.bot_config_manager import get_bot_config_manager
from src.services.background_tasks import start_background_tasks_for_team, stop_background_tasks
from src.services.bot_status_service import send_startup_messages, send_shutdown_messages
from telegram.ext import Application


class KICKAIRailwayApp:
    """Main Railway application that manages both bot and background tasks."""
    
    def __init__(self):
        self.bot_app: Optional[Application] = None
        self.team_id: Optional[str] = None
        self.bot_token: Optional[str] = None
        self.running = False
        self.shutdown_event = asyncio.Event()
    
    async def initialize(self) -> None:
        """Initialize the application."""
        try:
            logger.info("🚀 Initializing KICKAI Railway Application")
            
            # Get bot configuration
            manager = get_bot_config_manager()
            config = manager.load_configuration()
            
            # Get team ID
            self.team_id = config.default_team
            if not self.team_id and config.teams:
                self.team_id = list(config.teams.keys())[0]
                logger.info(f"📋 No default team set, using first available team: {self.team_id}")
            
            if not self.team_id:
                raise ValueError("❌ No teams found in configuration")
            
            # Get bot token
            bot_config = manager.get_bot_config(self.team_id)
            if not bot_config or not bot_config.token:
                raise ValueError(f"❌ No bot configuration found for team {self.team_id}")
            
            self.bot_token = bot_config.token
            
            logger.info(f"✅ Initialized for team: {self.team_id}")
            logger.info(f"✅ Bot token: {self.bot_token[:10]}...")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize application: {e}")
            raise
    
    async def start_background_tasks(self) -> None:
        """Start background tasks."""
        try:
            logger.info("🔄 Starting background tasks...")
            await start_background_tasks_for_team(self.team_id)
            logger.info("✅ Background tasks started")
        except Exception as e:
            logger.error(f"❌ Failed to start background tasks: {e}")
            # Don't raise - background tasks are optional
    
    async def start_telegram_bot(self) -> None:
        """Start the Telegram bot."""
        try:
            logger.info("🤖 Starting Telegram bot...")
            
            # Create bot application
            self.bot_app = Application.builder().token(self.bot_token).build()
            
            # Register unified message handler
            from src.telegram.unified_message_handler import register_unified_handler
            register_unified_handler(self.bot_app, self.team_id)
            logger.info("✅ Unified message handler registered")
            
            # Send startup message
            await send_startup_messages(self.bot_token, self.team_id)
            
            logger.info("✅ Telegram bot started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Telegram bot: {e}")
            raise
    
    def setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"📡 Received signal {signum}, initiating shutdown")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self) -> None:
        """Run the main application loop."""
        try:
            self.running = True
            self.setup_signal_handlers()
            
            # Start background tasks
            await self.start_background_tasks()
            
            # Start Telegram bot
            await self.start_telegram_bot()
            
            logger.info("🎉 KICKAI Railway Application is running!")
            logger.info("🤖 Telegram bot is active and listening for messages")
            logger.info("🔄 Background tasks are running")
            logger.info("💡 Send messages to your Telegram groups to test")
            logger.info("🛑 Press Ctrl+C to stop")
            
            # Keep the application running
            while self.running and not self.shutdown_event.is_set():
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ Error in main application loop: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self) -> None:
        """Shutdown the application gracefully."""
        if not self.running:
            return
        
        logger.info("🛑 Shutting down KICKAI Railway Application")
        self.running = False
        
        try:
            # Send shutdown message
            if self.bot_token and self.team_id:
                await send_shutdown_messages(self.bot_token, self.team_id)
            
            # Stop background tasks
            await stop_background_tasks()
            
            # Stop bot
            if self.bot_app:
                await self.bot_app.stop()
                await self.bot_app.shutdown()
            
            logger.info("✅ KICKAI Railway Application shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")


@asynccontextmanager
async def railway_app_context():
    """Context manager for Railway application lifecycle."""
    app = KICKAIRailwayApp()
    try:
        await app.initialize()
        yield app
    finally:
        await app.shutdown()


async def main():
    """Main entry point for Railway deployment."""
    try:
        async with railway_app_context() as app:
            await app.run()
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Application error: {e}")
        sys.exit(1)


def run():
    """Run the Railway application."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Failed to start Railway application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run() 