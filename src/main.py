#!/usr/bin/env python3
"""
Main Application Entry Point for KICKAI

This module provides the main application entry point with proper initialization,
error handling, and graceful shutdown.
"""

import asyncio
import signal
import sys
from typing import Optional, Any
from contextlib import asynccontextmanager
import logging

from .core.config import initialize_config, get_config
from .core.exceptions import ConfigurationError, KICKAIError
from .database.firebase_client import initialize_firebase_client, get_firebase_client
from .services.player_service import initialize_player_service
from .services.team_service import initialize_team_service


class KICKAIApplication:
    """Main KICKAI application class."""
    
    def __init__(self):
        self._logger: Optional[Any] = None
        self._firebase_client: Optional[Any] = None
        self._player_service: Optional[Any] = None
        self._team_service: Optional[Any] = None
        self._running = False
        self._shutdown_event = asyncio.Event()
    
    async def initialize(self) -> None:
        """Initialize the application."""
        try:
            # Initialize configuration
            config = initialize_config()
            
            # Initialize logging first
            logging.info("Logging system initialized")
            
            # Initialize Firebase client
            self._firebase_client = initialize_firebase_client(config.database)
            logging.info("Firebase client initialized")
            
            # Initialize services
            self._player_service = initialize_player_service()
            self._team_service = initialize_team_service()
            logging.info("Services initialized")
            
            # Perform health checks
            await self._perform_health_checks()
            
            logging.info("KICKAI application initialized successfully")
            
        except ConfigurationError as e:
            logging.error("Configuration error during initialization")
            raise
        except Exception as e:
            if self._logger:
                logging.error("Failed to initialize application")
            else:
                print(f"Failed to initialize application: {e}")
            raise
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks on all components."""
        try:
            # Database health check
            db_health = await self._firebase_client.health_check()
            if db_health['status'] != 'healthy':
                raise KICKAIError(f"Database health check failed: {db_health}")
            
            logging.info("Health checks passed")
            
        except Exception as e:
            logging.error("Health checks failed")
            raise
    
    async def start(self) -> None:
        """Start the application."""
        try:
            self._running = True
            logging.info("Starting KICKAI application")
            
            # Set up signal handlers
            self._setup_signal_handlers()
            
            # Start main application loop
            await self._main_loop()
            
        except Exception as e:
            logging.error("Error during application startup")
            raise
        finally:
            await self.shutdown()
    
    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logging.info(f"Received signal {signum}, initiating shutdown")
            self._shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def _main_loop(self) -> None:
        """Main application loop."""
        logging.info("Entering main application loop")
        
        try:
            while self._running and not self._shutdown_event.is_set():
                # Main application logic here
                # For now, just wait for shutdown signal
                await asyncio.sleep(1)
                
        except Exception as e:
            logging.error("Error in main loop")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the application gracefully."""
        if not self._running:
            return
        
        logging.info("Shutting down KICKAI application")
        self._running = False
        
        try:
            # Perform cleanup tasks
            await self._cleanup()
            
            logging.info("KICKAI application shutdown complete")
            
        except Exception as e:
            logging.error("Error during shutdown")
    
    async def _cleanup(self) -> None:
        """Perform cleanup tasks."""
        # Close database connections
        if self._firebase_client:
            # Firebase client doesn't need explicit cleanup
            pass
        
        # Close any other resources
        pass


@asynccontextmanager
async def application_context():
    """Context manager for application lifecycle."""
    app = KICKAIApplication()
    try:
        await app.initialize()
        yield app
    finally:
        await app.shutdown()


async def main():
    """Main entry point."""
    try:
        async with application_context() as app:
            await app.start()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)


def run():
    """Run the application."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
