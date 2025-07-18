"""
Dependency Container for the KICKAI application.

This module provides a centralized dependency injection container that manages
all service dependencies and ensures proper initialization order.
"""

import os
from typing import Dict, Any, Type, Optional
from database.interfaces import DataStoreInterface
from database.firebase_client import get_firebase_client
from database.mock_data_store import MockDataStore
from features.registry import create_service_factory, ServiceFactory


class DependencyContainer:
    """Centralized dependency injection container."""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._database: Optional[DataStoreInterface] = None
        self._factory: Optional[ServiceFactory] = None
        self._initialized = False
    
    def initialize(self):
        """Initialize the container with all required services."""
        if self._initialized:
            return
        
        # Phase 1: Initialize database first
        self._initialize_database()
        
        # Phase 2: Create service factory, passing the database explicitly
        self._factory = create_service_factory(self, self._database)
        
        # Phase 3: Create all services through factory
        self._factory.create_all_services()
        
        self._initialized = True
    
    def _initialize_database(self):
        """Initialize the database connection."""
        # Check if mock data store is enabled
        use_mock_datastore = os.getenv('USE_MOCK_DATASTORE', 'false').lower() == 'true'
        
        if use_mock_datastore:
            # Use mock data store for testing/development
            from core.logging_config import logger
            logger.info("🔧 Using Mock DataStore for development/testing")
            self._database = MockDataStore()
            
            # Initialize mock data store with default configurations
            self._initialize_mock_data()
        else:
            # Use real Firebase client
            from core.logging_config import logger
            logger.info("🔧 Using Firebase client for production/testing")
            firebase_client = get_firebase_client()
            self._database = firebase_client
        
        self._services[DataStoreInterface] = self._database
    
    def _initialize_mock_data(self):
        """Initialize mock data store with default configurations."""
        try:
            import asyncio
            from features.team_administration.domain.entities.team import Team, TeamStatus
            from datetime import datetime
            from core.logging_config import logger
            
            async def create_mock_team():
                # Create a mock team with bot configuration
                mock_team = Team(
                    id="KAI",
                    name="KickAI Testing",
                    status=TeamStatus.ACTIVE,
                    description="Test team for KICKAI bot",
                    created_by="system",
                    created_at=datetime.now(),
                    settings={
                        'bot_token': 'mock-bot-token-for-qa-testing',
                        'main_chat_id': '-1001234567890',
                        'leadership_chat_id': '-1001234567891',
                        'bot_username': 'kickai_testing_bot'
                    },
                    bot_id="KAI",
                    bot_token="mock-bot-token-for-qa-testing",
                    main_chat_id="-1001234567890",
                    leadership_chat_id="-1001234567891"
                )
                
                await self._database.create_team(mock_team)
                logger.info("✅ Mock team configuration created in data store")
            
            # Run the async function
            asyncio.run(create_mock_team())
            
        except Exception as e:
            from core.logging_config import logger
            logger.warning(f"⚠️ Failed to initialize mock data: {e}")
            # Continue without mock data - not critical for startup
    
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
    
    def register_service(self, interface: Type, implementation: Any):
        """Register a service implementation with its interface."""
        self._services[interface] = implementation
    
    def get_service(self, interface: Type) -> Any:
        """Get a service by its interface."""
        # Allow get_service to work during initialization, as long as the service is registered
        if interface not in self._services:
            raise RuntimeError(f"Service for interface {interface} not registered (container may not be fully initialized yet).")
        return self._services[interface]
    
    def has_service(self, interface: Type) -> bool:
        """Check if a service is registered."""
        if not self._initialized:
            return False
        return interface in self._services
    
    def get_all_services(self) -> Dict[Type, Any]:
        """Get all registered services."""
        if not self._initialized:
            return {}
        return self._services.copy()


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
def get_service(interface: Type) -> Any:
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
    container.initialize()
    return container 