#!/usr/bin/env python3
"""
Railway Web Server for KICKAI
Handles both web requests (for Railway health checks) and Telegram bot
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
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import threading


class KICKAIWebApp:
    """Web application that serves both HTTP requests and Telegram bot."""
    
    def __init__(self):
        self.bot_app: Optional[Application] = None
        self.team_id: Optional[str] = None
        self.bot_token: Optional[str] = None
        self.running = False
        self.shutdown_event = asyncio.Event()
        self.fastapi_app = FastAPI(title="KICKAI Bot", version="1.0.0")
        self.setup_routes()
    
    def setup_routes(self):
        """Set up FastAPI routes."""
        
        @self.fastapi_app.get("/")
        async def root():
            return {
                "status": "ok",
                "service": "KICKAI Telegram Bot",
                "environment": os.getenv("ENVIRONMENT", "unknown"),
                "team_id": self.team_id
            }
        
        @self.fastapi_app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "service": "KICKAI Telegram Bot",
                "environment": os.getenv("ENVIRONMENT", "unknown"),
                "bot_running": self.bot_app is not None,
                "team_id": self.team_id
            }
        
        @self.fastapi_app.get("/status")
        async def status():
            return {
                "status": "running",
                "service": "KICKAI Telegram Bot",
                "environment": os.getenv("ENVIRONMENT", "unknown"),
                "bot_running": self.bot_app is not None,
                "team_id": self.team_id,
                "railway_environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown")
            }
    
    async def initialize(self) -> None:
        """Initialize the application."""
        try:
            logger.info("🚀 Initializing KICKAI Web Application")
            
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
            if self.team_id:  # Add null check
                await start_background_tasks_for_team(self.team_id)
                logger.info("✅ Background tasks started")
            else:
                logger.warning("⚠️ Skipping background tasks - no team_id available")
        except Exception as e:
            logger.error(f"❌ Failed to start background tasks: {e}")
            # Don't raise - background tasks are optional
    
    async def start_telegram_bot(self) -> None:
        """Start the Telegram bot."""
        try:
            logger.info("🤖 Starting Telegram bot...")
            
            if not self.bot_token:
                logger.error("❌ No bot token available")
                return
            
            # Create bot application
            self.bot_app = Application.builder().token(self.bot_token).build()
            
            # Register unified message handler
            if self.team_id:  # Add null check
                from src.telegram.unified_message_handler import register_unified_handler
                register_unified_handler(self.bot_app, self.team_id)
                logger.info("✅ Unified message handler registered")
                
                # Send startup message
                await send_startup_messages(self.bot_token, self.team_id)
            else:
                logger.warning("⚠️ Skipping bot setup - no team_id available")
            
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
    
    async def run_bot(self) -> None:
        """Run the Telegram bot in a separate task."""
        try:
            if self.bot_app:
                await self.bot_app.initialize()
                await self.bot_app.start()
                await self.bot_app.updater.start_polling()
                
                logger.info("🤖 Telegram bot is polling for messages")
                
                # Keep the bot running
                while self.running and not self.shutdown_event.is_set():
                    await asyncio.sleep(1)
                    
        except Exception as e:
            logger.error(f"❌ Error in bot task: {e}")
            raise
    
    async def run(self) -> None:
        """Run the main application loop."""
        try:
            self.running = True
            self.setup_signal_handlers()
            
            # Start background tasks
            await self.start_background_tasks()
            
            # Start Telegram bot
            await self.start_telegram_bot()
            
            # Start bot polling in background
            bot_task = asyncio.create_task(self.run_bot())
            
            logger.info("🎉 KICKAI Web Application is running!")
            logger.info("🤖 Telegram bot is active and listening for messages")
            logger.info("🔄 Background tasks are running")
            logger.info("🌐 Web server is ready for health checks")
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
        
        logger.info("🛑 Shutting down KICKAI Web Application")
        self.running = False
        
        try:
            # Send shutdown message
            if self.bot_token and self.team_id:
                await send_shutdown_messages(self.bot_token, self.team_id)
            
            # Stop background tasks
            await stop_background_tasks()
            
            # Stop bot
            if self.bot_app:
                await self.bot_app.updater.stop()
                await self.bot_app.stop()
                await self.bot_app.shutdown()
            
            logger.info("✅ KICKAI Web Application shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")


# Global app instance
app_instance: Optional[KICKAIWebApp] = None


async def startup_event():
    """FastAPI startup event."""
    global app_instance
    app_instance = KICKAIWebApp()
    await app_instance.initialize()
    await app_instance.start_background_tasks()
    await app_instance.start_telegram_bot()
    
    # Start bot polling in background
    asyncio.create_task(app_instance.run_bot())


async def shutdown_event():
    """FastAPI shutdown event."""
    global app_instance
    if app_instance:
        await app_instance.shutdown()


def create_app():
    """Create the FastAPI application."""
    app = FastAPI(title="KICKAI Bot", version="1.0.0")
    
    @app.get("/")
    async def root():
        return {
            "status": "ok",
            "service": "KICKAI Telegram Bot",
            "environment": os.getenv("ENVIRONMENT", "unknown")
        }
    
    @app.get("/health")
    async def health():
        global app_instance
        return {
            "status": "healthy",
            "service": "KICKAI Telegram Bot",
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "bot_running": app_instance and app_instance.bot_app is not None,
            "team_id": app_instance.team_id if app_instance else None
        }
    
    @app.get("/status")
    async def status():
        global app_instance
        return {
            "status": "running",
            "service": "KICKAI Telegram Bot",
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "bot_running": app_instance and app_instance.bot_app is not None,
            "team_id": app_instance.team_id if app_instance else None,
            "railway_environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown")
        }
    
    app.add_event_handler("startup", startup_event)
    app.add_event_handler("shutdown", shutdown_event)
    
    return app


def main():
    """Main entry point for Railway deployment."""
    try:
        app = create_app()
        
        # Get port from Railway (Railway sets PORT automatically)
        port = int(os.getenv("PORT", 8080))
        
        logger.info(f"🚀 Starting KICKAI Web Server on port {port}")
        logger.info(f"🌐 Railway environment: {os.getenv('RAILWAY_ENVIRONMENT', 'unknown')}")
        logger.info(f"🔧 Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
        
        # Run with uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Application error: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main() 