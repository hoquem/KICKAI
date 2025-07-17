"""
Dependency Container for the KICKAI application.

This module provides a centralized dependency injection container that manages
all service dependencies and ensures proper initialization order.
"""

import os
from typing import Dict, Any, Type, Optional
from src.database.interfaces import DataStoreInterface
from src.database.firebase_client import get_firebase_client
from src.features.registry import create_service_factory, ServiceFactory


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
        
        # Initialize database first
        self._initialize_database()
        
        # Create service factory
        self._factory = create_service_factory(self)
        
        # Create all services through factory
        self._factory.create_all_services()
        
        self._initialized = True
    
    def _initialize_database(self):
        """Initialize the database connection."""
        # Initialize Firebase client using the proper function
        firebase_client = get_firebase_client()
        self._database = firebase_client
        self._services[DataStoreInterface] = firebase_client
    
    def get_database(self) -> DataStoreInterface:
        """Get the database interface."""
        if not self._initialized:
            self.initialize()
        return self._database
    
    def get_factory(self) -> ServiceFactory:
        """Get the service factory."""
        if not self._initialized:
            self.initialize()
        return self._factory
    
    def register_service(self, interface: Type, implementation: Any):
        """Register a service implementation with its interface."""
        self._services[interface] = implementation
    
    def get_service(self, interface: Type) -> Any:
        """Get a service by its interface."""
        if not self._initialized:
            self.initialize()
        
        if interface not in self._services:
            raise KeyError(f"Service {interface.__name__} not registered")
        
        return self._services[interface]
    
    def has_service(self, interface: Type) -> bool:
        """Check if a service is registered."""
        return interface in self._services
    
    def get_all_services(self) -> Dict[Type, Any]:
        """Get all registered services."""
        if not self._initialized:
            self.initialize()
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