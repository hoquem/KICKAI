#!/usr/bin/env python3
"""
KICKAI Main Entry Point using YAML-based configuration.

This is the main entry point for the KICKAI system using the new
YAML-based CrewAI configuration approach.
"""

import asyncio
import logging
from typing import Optional

from src.features.communication.infrastructure.telegram_bot_service import TelegramBotService
from src.core.dependency_container import initialize_container
from src.config.environment import load_environment
from crew import get_kickai_crew

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kickai.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class KICKAIMain:
    """
    Main KICKAI application using YAML-based configuration.
    
    This class initializes the system and manages the main application loop.
    """
    
    def __init__(self):
        """Initialize the KICKAI main application."""
        self.crew = None
        self.telegram_service = None
        
    async def initialize(self):
        """Initialize all system components."""
        try:
            logger.info("🚀 Initializing KICKAI system with YAML configuration...")
            
            # Load environment variables
            load_environment()
            logger.info("✅ Environment variables loaded")
            
            # Initialize dependency container
            initialize_container()
            logger.info("✅ Dependency container initialized")
            
            # Initialize YAML-based crew
            self.crew = get_kickai_crew()
            logger.info("✅ YAML-based crew initialized")
            
            # Initialize Telegram bot service
            self.telegram_service = TelegramBotService()
            await self.telegram_service.initialize()
            logger.info("✅ Telegram bot service initialized")
            
            logger.info("🎉 KICKAI system initialization complete!")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize KICKAI system: {e}")
            raise
    
    async def start(self):
        """Start the KICKAI system."""
        try:
            logger.info("🚀 Starting KICKAI system...")
            
            # Start the Telegram bot service
            await self.telegram_service.start()
            logger.info("✅ KICKAI system started successfully")
            
            # Keep the system running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("🛑 Received shutdown signal")
        except Exception as e:
            logger.error(f"❌ Error in main loop: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown the KICKAI system gracefully."""
        try:
            logger.info("🛑 Shutting down KICKAI system...")
            
            if self.telegram_service:
                await self.telegram_service.shutdown()
                logger.info("✅ Telegram bot service shutdown complete")
            
            logger.info("✅ KICKAI system shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")


async def main():
    """Main entry point for the KICKAI application."""
    app = KICKAIMain()
    
    try:
        await app.initialize()
        await app.start()
    except Exception as e:
        logger.error(f"❌ Fatal error in main: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Application terminated by user")
    except Exception as e:
        logger.error(f"❌ Fatal application error: {e}")
        exit(1) 