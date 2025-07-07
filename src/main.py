#!/usr/bin/env python3
"""
Main Application Entry Point for KICKAI

This module provides the main application entry point with proper initialization,
error handling, graceful shutdown, and comprehensive health monitoring.
"""

import asyncio
import signal
import sys
import time
import json
from typing import Optional, Any, Dict, List
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path
import traceback

from .core.config import initialize_config, get_config
from .core.exceptions import ConfigurationError, KICKAIError
from .database.firebase_client import initialize_firebase_client, get_firebase_client
from .services.player_service import initialize_player_service
from .services.team_service import initialize_team_service


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
            config = initialize_config()
            logging.info("Configuration initialized")
            
            # Initialize Firebase client
            self._firebase_client = initialize_firebase_client(config.database)
            logging.info("Firebase client initialized")
            
            # Test Firebase connection immediately
            await self._firebase_client.health_check()
            logging.info("Firebase connection verified")
            
            # Initialize services
            self._player_service = initialize_player_service()
            self._team_service = initialize_team_service()
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
    """Main entry point with comprehensive error handling."""
    try:
        async with application_context() as app:
            # Verify startup was successful
            if app.state != ApplicationState.READY:
                raise KICKAIError(f"Application failed to initialize properly: {app.state}")
            
            if not app.is_healthy:
                logging.warning("Application started but some components are unhealthy")
                unhealthy = [hc.component for hc in app._health_checks if hc.status != "healthy"]
                logging.warning(f"Unhealthy components: {unhealthy}")
            
            # Start the application
            await app.start()
            
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        sys.exit(0)
    except KICKAIError as e:
        print(f"KICKAI Application error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        logging.error(f"Unexpected error: {e}")
        logging.debug(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)


def run():
    """Run the application with proper error handling."""
    try:
        # Set up basic logging before anything else
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        sys.exit(0)
    except Exception as e:
        print(f"Failed to start application: {e}")
        logging.error(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import os
    run()