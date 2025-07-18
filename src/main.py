#!/usr/bin/env python3
"""
KICKAI Main Application Entry Point

This module provides the main entry point for the KICKAI football team management system.
It handles application lifecycle, health checks, and graceful shutdown.
"""

import asyncio
import json
import logging
import os
import signal
import sys
import time
import traceback
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional

# Import centralized logging configuration
from core.logging_config import (
    configure_logging, get_logger, LogContext, LogMessages,
    log_system_event, log_performance
)

# Import core components
from core.exceptions import KICKAIError
from features.system_infrastructure.domain.services.monitoring_service import MonitoringService
from features.team_administration.domain.services.multi_team_manager import MultiTeamManager
from database.firebase_client import FirebaseClient
from core.settings import get_settings
from core.command_registry import get_command_registry
from core.dependency_container import initialize_container
from core.logging_config import logging_config

from core.settings import initialize_settings, get_settings
from core.exceptions import ConfigurationError
from database.firebase_client import initialize_firebase_client, get_firebase_client
from features.player_registration.domain.services.player_service import PlayerService
from features.team_administration.domain.services.team_service import TeamService


class ApplicationState(Enum):
    """Application state enumeration."""
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class HealthStatus:
    """Health status for a component."""
    component: str
    status: str  # healthy, unhealthy, degraded, unknown
    message: str
    timestamp: float
    details: Optional[Dict[str, Any]] = None


@dataclass
class ApplicationStatus:
    """Overall application status."""
    state: ApplicationState
    startup_time: float
    uptime: float
    health_checks: List[HealthStatus]
    last_health_check: float
    pid: int
    version: str = "1.0.0"


class StartupValidator:
    """Validates that all components started correctly."""
    
    @staticmethod
    async def validate_services(app_instance) -> List[HealthStatus]:
        """Validate all services are properly initialized."""
        health_checks = []
        
        # Validate Firebase client
        if app_instance._firebase_client:
            try:
                db_health = await app_instance._firebase_client.health_check()
                health_checks.append(HealthStatus(
                    component="firebase_client",
                    status="healthy" if db_health.get('status') == 'healthy' else "unhealthy",
                    message=db_health.get('message', 'Database connection verified'),
                    timestamp=time.time(),
                    details=db_health
                ))
            except Exception as e:
                health_checks.append(HealthStatus(
                    component="firebase_client",
                    status="unhealthy",
                    message=f"Database health check failed: {str(e)}",
                    timestamp=time.time(),
                    details={"error": str(e)}
                ))
        else:
            health_checks.append(HealthStatus(
                component="firebase_client",
                status="unhealthy",
                message="Firebase client not initialized",
                timestamp=time.time()
            ))
        
        # Validate Player Service
        if app_instance._player_service:
            try:
                # Assume player service has a health check method
                health_checks.append(HealthStatus(
                    component="player_service",
                    status="healthy",
                    message="Player service initialized",
                    timestamp=time.time()
                ))
            except Exception as e:
                health_checks.append(HealthStatus(
                    component="player_service",
                    status="unhealthy",
                    message=f"Player service check failed: {str(e)}",
                    timestamp=time.time(),
                    details={"error": str(e)}
                ))
        else:
            health_checks.append(HealthStatus(
                component="player_service",
                status="unhealthy",
                message="Player service not initialized",
                timestamp=time.time()
            ))
        
        # Validate Team Service
        if app_instance._team_service:
            try:
                health_checks.append(HealthStatus(
                    component="team_service",
                    status="healthy",
                    message="Team service initialized",
                    timestamp=time.time()
                ))
            except Exception as e:
                health_checks.append(HealthStatus(
                    component="team_service",
                    status="unhealthy",
                    message=f"Team service check failed: {str(e)}",
                    timestamp=time.time(),
                    details={"error": str(e)}
                ))
        else:
            health_checks.append(HealthStatus(
                component="team_service",
                status="unhealthy",
                message="Team service not initialized",
                timestamp=time.time()
            ))
        
        return health_checks


class KICKAIApplication:
    """Main KICKAI application class with enhanced resilience."""
    
    def __init__(self):
        self._logger: Optional[Any] = None
        self._firebase_client: Optional[Any] = None
        self._player_service: Optional[Any] = None
        self._team_service: Optional[Any] = None
        self._running = False
        self._shutdown_event = asyncio.Event()
        self._startup_time: Optional[float] = None
        self._state = ApplicationState.INITIALIZING
        self._health_checks: List[HealthStatus] = []
        self._last_health_check = 0.0
        self._status_file = Path("kickai_status.json")
        self._health_check_interval = 30.0  # seconds
        self._startup_timeout = 60.0  # seconds
        self._max_startup_retries = 3
        self._startup_retry_delay = 5.0  # seconds
    
    @property
    def state(self) -> ApplicationState:
        """Get current application state."""
        return self._state
    
    @property
    def is_healthy(self) -> bool:
        """Check if application is healthy."""
        if not self._health_checks:
            return False
        return all(hc.status == "healthy" for hc in self._health_checks)
    
    async def initialize(self) -> None:
        """Initialize the application with retries and validation."""
        self._startup_time = time.time()
        self._state = ApplicationState.INITIALIZING
        
        for attempt in range(self._max_startup_retries):
            try:
                logging.info(f"Initializing KICKAI application (attempt {attempt + 1}/{self._max_startup_retries})")
                
                # Initialize with timeout
                await asyncio.wait_for(
                    self._initialize_components(),
                    timeout=self._startup_timeout
                )
                
                # Validate startup
                await self._validate_startup()
                
                self._state = ApplicationState.READY
                logging.info("KICKAI application initialized successfully")
                await self._write_status_file()
                return
                
            except asyncio.TimeoutError:
                logging.error(f"Initialization timeout on attempt {attempt + 1}")
                self._state = ApplicationState.ERROR
                if attempt < self._max_startup_retries - 1:
                    await asyncio.sleep(self._startup_retry_delay)
                    continue
                raise KICKAIError("Application initialization timed out")
                
            except Exception as e:
                logging.error(f"Initialization failed on attempt {attempt + 1}: {str(e)}")
                logging.debug(f"Full traceback: {traceback.format_exc()}")
                self._state = ApplicationState.ERROR
                if attempt < self._max_startup_retries - 1:
                    await asyncio.sleep(self._startup_retry_delay)
                    continue
                raise
        
        # If we get here, all retries failed
        self._state = ApplicationState.ERROR
        raise KICKAIError("Application initialization failed after all retries")
    
    async def _initialize_components(self) -> None:
        """Initialize all application components."""
        try:
            # Initialize configuration
            initialize_settings()
            config = get_settings()
            logging.info("Configuration initialized")
            
            # Initialize Firebase client
            self._firebase_client = initialize_firebase_client(config)
            logging.info("Firebase client initialized")
            
            # Test Firebase connection immediately
            await self._firebase_client.health_check()
            logging.info("Firebase connection verified")
            
            # Initialize services
            self._player_service = PlayerService()
            self._team_service = TeamService()
            logging.info("Services initialized")
            
        except Exception as e:
            logging.error(f"Component initialization failed: {str(e)}")
            raise
    
    async def _validate_startup(self) -> None:
        """Validate that all components started correctly."""
        try:
            # Perform comprehensive health checks
            self._health_checks = await StartupValidator.validate_services(self)
            self._last_health_check = time.time()
            
            # Check if any critical components are unhealthy
            critical_failures = [
                hc for hc in self._health_checks 
                if hc.status == "unhealthy" and hc.component in ["firebase_client"]
            ]
            
            if critical_failures:
                error_msg = f"Critical component failures: {[hc.component for hc in critical_failures]}"
                logging.error(error_msg)
                raise KICKAIError(error_msg)
            
            # Log health status
            healthy_count = sum(1 for hc in self._health_checks if hc.status == "healthy")
            total_count = len(self._health_checks)
            logging.info(f"Health validation complete: {healthy_count}/{total_count} components healthy")
            
            # Log any degraded components
            degraded = [hc for hc in self._health_checks if hc.status == "degraded"]
            if degraded:
                logging.warning(f"Degraded components: {[hc.component for hc in degraded]}")
            
        except Exception as e:
            logging.error(f"Startup validation failed: {str(e)}")
            raise
    
    async def start(self) -> None:
        """Start the application."""
        try:
            self._running = True
            self._state = ApplicationState.RUNNING
            logging.info("Starting KICKAI application")
            
            # Set up signal handlers
            self._setup_signal_handlers()
            
            # Start background tasks
            health_check_task = asyncio.create_task(self._health_check_loop())
            status_update_task = asyncio.create_task(self._status_update_loop())
            
            try:
                # Start main application loop
                await self._main_loop()
            finally:
                # Cancel background tasks
                health_check_task.cancel()
                status_update_task.cancel()
                
                # Wait for tasks to complete
                await asyncio.gather(
                    health_check_task, 
                    status_update_task, 
                    return_exceptions=True
                )
            
        except Exception as e:
            logging.error(f"Error during application startup: {str(e)}")
            self._state = ApplicationState.ERROR
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
        """Main application loop with error handling."""
        logging.info("Entering main application loop")
        
        try:
            while self._running and not self._shutdown_event.is_set():
                # Main application logic here
                # Add your core business logic
                await asyncio.sleep(1)
                
        except Exception as e:
            logging.error(f"Error in main loop: {str(e)}")
            self._state = ApplicationState.ERROR
            raise
    
    async def _health_check_loop(self) -> None:
        """Background health check loop."""
        while self._running and not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self._health_check_interval)
                
                # Perform health checks
                self._health_checks = await StartupValidator.validate_services(self)
                self._last_health_check = time.time()
                
                # Log health status
                if not self.is_healthy:
                    unhealthy = [hc.component for hc in self._health_checks if hc.status != "healthy"]
                    logging.warning(f"Health check: unhealthy components: {unhealthy}")
                else:
                    logging.debug("Health check: all components healthy")
                
            except Exception as e:
                logging.error(f"Health check failed: {str(e)}")
    
    async def _status_update_loop(self) -> None:
        """Background status file update loop."""
        while self._running and not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(10)  # Update every 10 seconds
                await self._write_status_file()
            except Exception as e:
                logging.error(f"Status update failed: {str(e)}")
    
    async def _write_status_file(self) -> None:
        """Write current status to file."""
        try:
            uptime = time.time() - self._startup_time if self._startup_time else 0
            
            status = ApplicationStatus(
                state=self._state,
                startup_time=self._startup_time or 0,
                uptime=uptime,
                health_checks=self._health_checks,
                last_health_check=self._last_health_check,
                pid=os.getpid()
            )
            
            with open(self._status_file, 'w') as f:
                json.dump(asdict(status), f, indent=2, default=str)
                
        except Exception as e:
            logging.error(f"Failed to write status file: {str(e)}")
    
    async def shutdown(self) -> None:
        """Shutdown the application gracefully."""
        if self._state == ApplicationState.STOPPED:
            return
        
        logging.info("Shutting down KICKAI application")
        self._state = ApplicationState.STOPPING
        self._running = False
        
        try:
            # Perform cleanup tasks
            await self._cleanup()
            
            self._state = ApplicationState.STOPPED
            await self._write_status_file()
            logging.info("KICKAI application shutdown complete")
            
        except Exception as e:
            logging.error(f"Error during shutdown: {str(e)}")
            self._state = ApplicationState.ERROR
    
    async def _cleanup(self) -> None:
        """Perform cleanup tasks."""
        try:
            # Close database connections
            if self._firebase_client:
                # Firebase client doesn't need explicit cleanup
                pass
            
            # Close any other resources
            pass
            
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current application status."""
        uptime = time.time() - self._startup_time if self._startup_time else 0
        
        return {
            "state": self._state.value,
            "startup_time": self._startup_time,
            "uptime": uptime,
            "is_healthy": self.is_healthy,
            "health_checks": [asdict(hc) for hc in self._health_checks],
            "last_health_check": self._last_health_check,
            "pid": os.getpid()
        }


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
    """Main entry point for the KICKAI bot."""
    try:
        # Initialize logging
        logging_config.configure_logging()
        logger = get_logger(__name__)
        logger.info("✅ Configuration loaded successfully and logging configured")
        
        # Initialize Firebase client
        firebase_client = get_firebase_client()
        logger.info("✅ Firebase client initialized")
        
        # Initialize dependency container
        initialize_container(firebase_client)
        logger.info("✅ Dependency container initialized with Firebase client")
        
        # Initialize unified command registry
        command_registry = get_command_registry()
        command_registry.auto_discover_commands()
        logger.info("✅ Unified command registry initialized")
        
        # Create multi-bot manager
        multi_bot_manager = MultiTeamManager(firebase_client)
        logger.info("✅ Multi-bot manager created with bot configurations")
        
        # Start all bots
        await multi_bot_manager.start_all_bots()
        logger.info("🤖 Multi-bot manager is running. Press Ctrl+C to exit.")
        
        # Keep the bot running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger = get_logger(__name__)
        logger.info("🛑 Received shutdown signal, initiating graceful shutdown...")
        # The original code had a shutdown() call here, but shutdown() is part of KICKAIApplication.
        # Since the main function is now directly managing the bot loop,
        # we need to ensure the application context is properly handled.
        # For now, we'll just print a message and exit gracefully.
        sys.exit(0)
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"❌ Fatal error in main: {e}", exc_info=True)
        # The original code had a shutdown() call here, but shutdown() is part of KICKAIApplication.
        # Since the main function is now directly managing the bot loop,
        # we need to ensure the application context is properly handled.
        # For now, we'll just print a message and exit gracefully.
        sys.exit(1)


def run():
    """Run the application with proper error handling and centralized logging."""
    try:
        # Configure centralized logging system
        configure_logging(
            log_level=os.getenv('KICKAI_LOG_LEVEL', 'INFO'),
            log_format=os.getenv('KICKAI_LOG_FORMAT', 'text'),
            log_file=os.getenv('KICKAI_LOG_FILE', 'logs/kickai.log'),
            include_context=True
        )
        
        # Get application logger
        logger = get_logger(__name__)
        
        # Log system startup
        log_system_event(LogMessages.SYSTEM_STARTUP, 
                        context=LogContext(component="main"))
        
        # Run the application
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger = get_logger(__name__)
        logger.info("🛑 Shutdown requested by user")
        log_system_event("Application shutdown requested by user", 
                        context=LogContext(component="main"))
        sys.exit(0)
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Failed to start application: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run()