"""
Dependency Container for the KICKAI application.

This module provides a centralized dependency injection container that manages
all service dependencies and ensures proper initialization order.
"""

import os
from typing import Any, Optional, Union

from kickai.database.firebase_client import get_firebase_client
from kickai.database.interfaces import DataStoreInterface
from kickai.database.mock_data_store import MockDataStore
from kickai.features.registry import ServiceFactory, create_service_factory


class DependencyContainer:
    """Centralized dependency injection container."""

    def __init__(self):
        self._services: dict[type, Any] = {}
        self._database: Optional[DataStoreInterface] = None
        self._factory: Optional[ServiceFactory] = None
        self._initialized = False

    async def initialize(self):
        """Initialize the container with all required services."""
        if self._initialized:
            return

        # Phase 1: Initialize database first
        self._initialize_database()

        # Phase 2: Create service factory, passing the database explicitly
        self._factory = create_service_factory(self, self._database)

        # Phase 3: Create all services through factory
        self._factory.create_all_services()

        # Phase 4: Initialize team config cache for performance optimization
        await self._initialize_team_config_cache()

        self._initialized = True

    async def _initialize_team_config_cache(self):
        """Initialize the team config cache at startup for optimal performance."""
        try:
            from kickai.core.team_config_cache import TeamConfigCache
            from kickai.core.logging_config import logger
            
            # Get cache instance and initialize it
            cache = TeamConfigCache()
            await cache.initialize()
            
            # Register the cache as a singleton service
            self.register_service(TeamConfigCache, cache)
            
            logger.info("✅ Team config cache initialized and registered")
            
        except Exception as e:
            from kickai.core.logging_config import logger
            logger.warning(f"⚠️ Team config cache initialization failed: {e}")
            logger.info("🔄 System will fall back to database queries for team config")
            # Don't fail startup - system can work without cache

    def _initialize_database(self):
        """Initialize the database connection."""
        # Check if mock data store is enabled
        use_mock_datastore = os.getenv("USE_MOCK_DATASTORE", "false").lower() == "true"

        if use_mock_datastore:
            # Use mock data store for testing/development
            from kickai.core.logging_config import logger

            logger.info("🔧 Using Mock DataStore for development/testing")
            self._database = MockDataStore()
            
            # Mock data will be created on-demand by MockDataStore when accessed
            logger.info("✅ Mock data store ready (on-demand initialization)")
        else:
            # Use real Firebase client
            from kickai.core.logging_config import logger

            logger.info("🔧 Using Firebase client for production/testing")
            firebase_client = get_firebase_client()
            self._database = firebase_client

        self._services[DataStoreInterface] = self._database

# Removed _initialize_mock_data() - was redundant after removing asyncio.run()

    def verify_services_ready(self) -> bool:
        """Verify that all required services are registered and ready."""
        # Import the actual service classes that are being registered
        try:
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
                    service = self.get_service(service_class)
                    if service is None:
                        missing_services.append(service_class.__name__)
                except Exception:
                    missing_services.append(service_class.__name__)

            if missing_services:
                from kickai.core.logging_config import logger

                logger.error(f"❌ Missing required services: {missing_services}")
                return False

            return True

        except Exception as e:
            from kickai.core.logging_config import logger

            logger.error(f"❌ Service verification failed: {e}")
            return False

    def get_database(self) -> DataStoreInterface:
        """Get the database interface."""
        if not self._initialized and self._database is None:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._database

    def get_factory(self) -> ServiceFactory:
        """Get the service factory."""
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._factory

    def register_service(self, interface: type, implementation: Any):
        """Register a service implementation with its interface."""
        self._services[interface] = implementation

    def update_service(self, interface: type, implementation: Any):
        """Update an existing service implementation."""
        if interface in self._services:
            self._services[interface] = implementation
        else:
            self._services[interface] = implementation

    def get_service(self, interface: Union[type, str]) -> Any:
        """Get a service by its interface or name."""
        # Handle string-based service lookup
        if isinstance(interface, str):
            # Try to find by name in registered services
            for service_type, service in self._services.items():
                if service_type.__name__ == interface:
                    return service
            # If not found and container is initialized, raise error
            if self._initialized:
                raise RuntimeError(f"Service '{interface}' not registered.")
            else:
                raise RuntimeError(
                    f"Service '{interface}' not registered (container may not be fully initialized yet)."
                )

        # Handle type-based service lookup (original behavior)
        if interface not in self._services:
            if not self._initialized:
                raise RuntimeError(
                    f"Service for interface {interface} not registered (container may not be fully initialized yet)."
                )
            else:
                raise RuntimeError(f"Service for interface {interface} not registered.")
        return self._services[interface]

    def has_service(self, interface: type) -> bool:
        """Check if a service is registered."""
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return interface in self._services

    def get_all_services(self) -> dict[type, Any]:
        """Get all registered services."""
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._services.copy()


# Global container instance
_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """Get the global dependency container instance."""
    global _container
    if _container is None:
        _container = DependencyContainer()
    return _container


async def initialize_container():
    """Initialize the global container."""
    container = get_container()
    await container.initialize()
    return container


# Backward compatibility functions
def get_service(interface: type) -> Any:
    """Get a service by its interface (backward compatibility)."""
    container = get_container()
    return container.get_service(interface)


def get_singleton(name: str) -> Any:
    """Get a singleton service by name (backward compatibility)."""
    container = get_container()

    # Map common singleton names to their interfaces
    singleton_map = {
        "data_store": DataStoreInterface,
        "database": DataStoreInterface,
    }

    if name in singleton_map:
        return container.get_service(singleton_map[name])

    # Try to find by name in registered services
    for service_type, service in container.get_all_services().items():
        if service_type.__name__.lower() == name.lower():
            return service

    raise KeyError(f"Singleton '{name}' not found")


def ensure_container_initialized():
    """Ensure the container is initialized (backward compatibility)."""
    container = get_container()
    if not container._initialized:
        # For backward compatibility with sync code, initialize without cache
        container._initialize_database()
        container._factory = create_service_factory(container, container._database)
        container._factory.create_all_services()
        container._initialized = True
    return container

async def ensure_container_initialized_async():
    """Ensure the container is initialized with team config cache (async version)."""
    container = get_container()
    if not container._initialized:
        await container.initialize()
    return container
