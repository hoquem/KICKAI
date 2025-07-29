#!/usr/bin/env python3
"""
Service Interfaces

Interfaces for different types of services following the Interface Segregation Principle.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class IServiceRegistry(ABC):
    """Interface for service registration and retrieval."""
    
    @abstractmethod
    def register_service(self, interface: type, implementation: Any) -> None:
        """Register a service implementation with its interface."""
        pass
    
    @abstractmethod
    def get_service(self, interface: type) -> Any:
        """Get a service by its interface."""
        pass
    
    @abstractmethod
    def has_service(self, interface: type) -> bool:
        """Check if a service is registered."""
        pass


class IServiceFactory(ABC):
    """Interface for service factory operations."""
    
    @abstractmethod
    def create_service(self, service_type: type, **kwargs) -> Any:
        """Create a service instance."""
        pass
    
    @abstractmethod
    def get_factory_info(self) -> Dict[str, Any]:
        """Get information about the factory."""
        pass


class IDatabaseManager(ABC):
    """Interface for database management operations."""
    
    @abstractmethod
    def initialize_database(self) -> None:
        """Initialize the database connection."""
        pass
    
    @abstractmethod
    def get_database(self) -> Any:
        """Get the database interface."""
        pass
    
    @abstractmethod
    def verify_database_connection(self) -> bool:
        """Verify database connection is working."""
        pass


class IContainerLifecycle(ABC):
    """Interface for container lifecycle management."""
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the container."""
        pass
    
    @abstractmethod
    def is_initialized(self) -> bool:
        """Check if container is initialized."""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset the container state."""
        pass
    
    @abstractmethod
    def verify_services_ready(self) -> bool:
        """Verify all required services are ready."""
        pass


class IStringServiceLookup(ABC):
    """Interface for string-based service lookup."""
    
    @abstractmethod
    def get_service_by_name(self, service_name: str) -> Any:
        """Get a service by its name."""
        pass
    
    @abstractmethod
    def get_singleton(self, name: str) -> Any:
        """Get a singleton service by name."""
        pass


class IContainerStatistics(ABC):
    """Interface for container statistics and monitoring."""
    
    @abstractmethod
    def get_service_count(self) -> int:
        """Get the number of registered services."""
        pass
    
    @abstractmethod
    def get_service_names(self) -> list[str]:
        """Get list of registered service names."""
        pass
    
    @abstractmethod
    def get_container_status(self) -> Dict[str, Any]:
        """Get container status information."""
        pass