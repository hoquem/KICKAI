"""
Dependency Container for the KICKAI application.

This module provides a centralized dependency injection container that manages
all service dependencies and ensures proper initialization order.
"""

from typing import Any, Dict, Optional

from loguru import logger

from kickai.core.database.database_manager import DatabaseManager
from kickai.core.interfaces.service_interfaces import (
    IContainerLifecycle,
    IContainerStatistics,
    IDatabaseManager,
    IServiceRegistry,
)
from kickai.core.registry.service_registry import ServiceRegistry
from kickai.database.interfaces import DataStoreInterface
from kickai.features.registry import ServiceFactory, create_service_factory


class DependencyContainer(IContainerLifecycle, IContainerStatistics):
    """Centralized dependency injection container with improved architecture."""

    def __init__(self):
        # Initialize specialized components
        self._service_registry = ServiceRegistry()
        self._database_manager = DatabaseManager()
        self._factory: Optional[ServiceFactory] = None
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the container with all required services."""
        if self._initialized:
            logger.info("🔧 DependencyContainer: Container already initialized")
            return

        try:
            logger.info("🔧 DependencyContainer: Starting initialization...")

            # Phase 1: Initialize database first
            self._database_manager.initialize_database()
            database = self._database_manager.get_database()
            self._service_registry.register_service(DataStoreInterface, database)

            # Phase 2: Create service factory, passing the database explicitly
            self._factory = create_service_factory(self, database)

            # Phase 3: Create all services through factory
            self._factory.create_all_services()

            # Mark as initialized before verification to prevent circular calls
            self._initialized = True
            logger.info("✅ DependencyContainer: Initialization completed successfully")

        except Exception as e:
            logger.error(f"❌ DependencyContainer: Initialization failed: {e}")
            self._initialized = False
            raise

    def is_initialized(self) -> bool:
        """Check if container is initialized."""
        return self._initialized

    def reset(self) -> None:
        """Reset the container state."""
        try:
            self._service_registry.clear_services()
            self._factory = None
            self._initialized = False
            logger.info("🔄 DependencyContainer: Container reset completed")
        except Exception as e:
            logger.error(f"❌ DependencyContainer: Reset failed: {e}")
            raise

    def verify_services_ready(self) -> bool:
        """Verify that all required services are registered and ready."""
        try:
            # Import the actual service classes that are being registered
            from kickai.database.interfaces import DataStoreInterface
            from kickai.features.player_registration.domain.services.player_service import (
                PlayerService,
            )
            from kickai.features.team_administration.domain.services.team_member_service import (
                TeamMemberService,
            )
            from kickai.features.team_administration.domain.services.team_service import TeamService

            required_services = [PlayerService, TeamMemberService, TeamService, DataStoreInterface]

            missing_services = []
            for service_class in required_services:
                try:
                    # Check directly in the registry instead of going through get_service
                    if not self._service_registry.has_service(service_class):
                        missing_services.append(service_class.__name__)
                except Exception:
                    missing_services.append(service_class.__name__)

            if missing_services:
                logger.error(f"❌ DependencyContainer: Missing required services: {missing_services}")
                return False

            logger.info("✅ DependencyContainer: All required services verified")
            return True

        except Exception as e:
            logger.error(f"❌ DependencyContainer: Service verification failed: {e}")
            return False

    # Database management methods
    def get_database(self) -> DataStoreInterface:
        """Get the database interface."""
        return self._database_manager.get_database()

    def verify_database_connection(self) -> bool:
        """Verify database connection is working."""
        return self._database_manager.verify_database_connection()

    # Service factory methods
    def get_factory(self) -> ServiceFactory:
        """Get the service factory."""
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._factory

    # Service registry methods (delegated to ServiceRegistry)
    def register_service(self, interface: type, implementation: Any) -> None:
        """Register a service implementation with its interface."""
        self._service_registry.register_service(interface, implementation)

    def get_service(self, interface) -> Any:
        """Get a service by its interface or name."""
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._service_registry.get_service(interface)

    def has_service(self, interface: type) -> bool:
        """Check if a service is registered."""
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._service_registry.has_service(interface)

    def get_all_services(self) -> Dict[type, Any]:
        """Get all registered services."""
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._service_registry.get_all_services()

    # String-based service lookup methods
    def get_service_by_name(self, service_name: str) -> Any:
        """Get a service by its name."""
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._service_registry.get_service_by_name(service_name)

    def get_singleton(self, name: str) -> Any:
        """Get a singleton service by name."""
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._service_registry.get_singleton(name)

    # Container statistics methods
    def get_service_count(self) -> int:
        """Get the number of registered services."""
        return self._service_registry.get_service_count()

    def get_service_names(self) -> list[str]:
        """Get list of registered service names."""
        return self._service_registry.get_service_names()

    def get_container_status(self) -> Dict[str, Any]:
        """Get container status information."""
        try:
            return {
                "initialized": self._initialized,
                "service_count": self.get_service_count(),
                "service_names": self.get_service_names(),
                "database_initialized": self._database_manager.is_initialized(),
                "database_connection_verified": self._database_manager.verify_database_connection() if self._database_manager.is_initialized() else False,
            }
        except Exception as e:
            logger.error(f"❌ DependencyContainer: Error getting container status: {e}")
            return {
                "initialized": self._initialized,
                "service_count": 0,
                "service_names": [],
                "database_initialized": False,
                "database_connection_verified": False,
                "error": str(e)
            }

    # Backward compatibility methods
    def update_service(self, interface: type, implementation: Any) -> None:
        """Update an existing service implementation."""
        self._service_registry.update_service(interface, implementation)


# Global container instance
_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """Get the global dependency container instance."""
    global _container
    if _container is None:
        _container = DependencyContainer()
    return _container


def initialize_container():
    """Initialize the global container."""
    container = get_container()
    container.initialize()
    return container


# Backward compatibility functions
def get_service(interface: type) -> Any:
    """Get a service by its interface (backward compatibility)."""
    container = get_container()
    return container.get_service(interface)


def get_singleton(name: str) -> Any:
    """Get a singleton service by name (backward compatibility)."""
    container = get_container()
    return container.get_singleton(name)


def ensure_container_initialized():
    """Ensure the container is initialized (backward compatibility)."""
    container = get_container()
    if not container.is_initialized():
        container.initialize()
    return container
