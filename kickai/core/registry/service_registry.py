#!/usr/bin/env python3
"""
Service Registry

Dedicated class for service registration and retrieval following the Single Responsibility Principle.
"""

from typing import Any

from loguru import logger

from kickai.core.interfaces.service_interfaces import IServiceRegistry, IStringServiceLookup


class ServiceRegistry(IServiceRegistry, IStringServiceLookup):
    """Manages service registration and retrieval."""

    def __init__(self):
        self._services: dict[type, Any] = {}
        self._service_names: dict[str, type] = {}  # name -> type mapping

    def register_service(self, interface: type, implementation: Any) -> None:
        """Register a service implementation with its interface."""
        try:
            self._services[interface] = implementation
            self._service_names[interface.__name__] = interface
            logger.info(f"✅ ServiceRegistry: Registered service {interface.__name__}")
        except Exception as e:
            logger.error(f"❌ ServiceRegistry: Failed to register service {interface.__name__}: {e}")
            raise

    def get_service(self, interface: type | str) -> Any:
        """Get a service by its interface or name."""
        try:
            # Handle string-based service lookup
            if isinstance(interface, str):
                return self.get_service_by_name(interface)

            # Handle type-based service lookup
            if interface not in self._services:
                raise RuntimeError(f"Service for interface {interface} not registered.")

            return self._services[interface]

        except Exception as e:
            logger.error(f"❌ ServiceRegistry: Failed to get service {interface}: {e}")
            raise

    def has_service(self, interface: type) -> bool:
        """Check if a service is registered."""
        return interface in self._services

    def get_service_by_name(self, service_name: str) -> Any:
        """Get a service by its name."""
        try:
            # Try to find by name in registered services
            for service_type, service in self._services.items():
                if service_type.__name__ == service_name:
                    return service

            # If not found, raise error
            raise RuntimeError(f"Service '{service_name}' not registered.")

        except Exception as e:
            logger.error(f"❌ ServiceRegistry: Failed to get service by name '{service_name}': {e}")
            raise

    def get_singleton(self, name: str) -> Any:
        """Get a singleton service by name."""
        try:
            # Map common singleton names to their interfaces
            singleton_map = {
                "data_store": "DataStoreInterface",
                "database": "DataStoreInterface",
            }

            if name in singleton_map:
                return self.get_service_by_name(singleton_map[name])

            # Try to find by name in registered services
            for service_type, service in self._services.items():
                if service_type.__name__.lower() == name.lower():
                    return service

            raise KeyError(f"Singleton '{name}' not found")

        except Exception as e:
            logger.error(f"❌ ServiceRegistry: Failed to get singleton '{name}': {e}")
            raise

    def update_service(self, interface: type, implementation: Any) -> None:
        """Update an existing service implementation."""
        try:
            if interface in self._services:
                logger.info(f"🔄 ServiceRegistry: Updating existing service {interface.__name__}")
            else:
                logger.info(f"✅ ServiceRegistry: Adding new service {interface.__name__}")

            self._services[interface] = implementation
            self._service_names[interface.__name__] = interface

        except Exception as e:
            logger.error(f"❌ ServiceRegistry: Failed to update service {interface.__name__}: {e}")
            raise

    def get_all_services(self) -> dict[type, Any]:
        """Get all registered services."""
        return self._services.copy()

    def get_service_names(self) -> list[str]:
        """Get list of registered service names."""
        return list(self._service_names.keys())

    def get_service_count(self) -> int:
        """Get the number of registered services."""
        return len(self._services)

    def clear_services(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._service_names.clear()
        logger.info("🔄 ServiceRegistry: All services cleared")
