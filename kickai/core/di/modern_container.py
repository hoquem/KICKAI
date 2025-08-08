"""
Modern dependency injection container.

This module provides a modern DI container with scoping,
lifecycle management, and auto-wiring capabilities.
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, TypeVar

from loguru import logger

T = TypeVar("T")


class ServiceScope(Enum):
    """Service lifecycle scopes."""

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    REQUEST = "request"


@dataclass
class ServiceRegistration:
    """Service registration metadata."""

    interface: type
    implementation: Optional[type] = None
    scope: ServiceScope = ServiceScope.SINGLETON
    factory: Optional[Callable] = None
    dependencies: list[type] | None = None


class ModernDIContainer:
    """Modern dependency injection container with scoping and lifecycle management."""

    def __init__(self):
        self._registrations: dict[type, ServiceRegistration] = {}
        self._singletons: dict[type, Any] = {}
        self._request_scope: dict[type, Any] = {}
        self._initialized = False

        logger.info("🔧 Modern DI Container initialized")

    def register_singleton(self, interface: type[T], implementation: type[T]) -> None:
        """Register a singleton service."""
        self._registrations[interface] = ServiceRegistration(
            interface=interface, implementation=implementation, scope=ServiceScope.SINGLETON
        )
        logger.debug(f"📝 Registered singleton: {interface.__name__}")

    def register_transient(self, interface: type[T], implementation: type[T]) -> None:
        """Register a transient service."""
        self._registrations[interface] = ServiceRegistration(
            interface=interface, implementation=implementation, scope=ServiceScope.TRANSIENT
        )
        logger.debug(f"📝 Registered transient: {interface.__name__}")

    def register_factory(self, interface: type[T], factory: Callable) -> None:
        """Register a factory-based service."""
        self._registrations[interface] = ServiceRegistration(
            interface=interface, scope=ServiceScope.TRANSIENT, factory=factory
        )
        logger.debug(f"📝 Registered factory: {interface.__name__}")

    def resolve(self, interface: type[T]) -> T:
        """Resolve a service instance."""
        if interface not in self._registrations:
            raise KeyError(f"Service {interface.__name__} not registered")

        registration = self._registrations[interface]

        if registration.scope == ServiceScope.SINGLETON:
            if interface not in self._singletons:
                self._singletons[interface] = self._create_instance(registration)
            return self._singletons[interface]

        elif registration.scope == ServiceScope.TRANSIENT:
            return self._create_instance(registration)

        elif registration.scope == ServiceScope.REQUEST:
            if interface not in self._request_scope:
                self._request_scope[interface] = self._create_instance(registration)
            return self._request_scope[interface]

    def _create_instance(self, registration: ServiceRegistration) -> Any:
        """Create a service instance."""
        if registration.factory:
            return registration.factory()

        if not registration.implementation:
            raise ValueError(f"No implementation or factory for {registration.interface.__name__}")

        # Auto-wire dependencies
        if hasattr(registration.implementation, "__init__"):
            import inspect

            sig = inspect.signature(registration.implementation.__init__)
            dependencies = {}

            for param_name, param in sig.parameters.items():
                if param_name != "self" and param.annotation != inspect.Parameter.empty:
                    try:
                        dependencies[param_name] = self.resolve(param.annotation)
                    except Exception as e:
                        logger.error(f"❌ Failed to resolve dependency {param_name}: {e}")
                        raise

            return registration.implementation(**dependencies)

        return registration.implementation()

    def begin_request_scope(self) -> None:
        """Begin a new request scope."""
        self._request_scope.clear()
        logger.debug("🔄 Request scope begun")

    def end_request_scope(self) -> None:
        """End the current request scope."""
        self._request_scope.clear()
        logger.debug("🔄 Request scope ended")

    def validate(self) -> list[str]:
        """Validate container configuration."""
        errors = []

        for interface, registration in self._registrations.items():
            if not registration.implementation and not registration.factory:
                errors.append(f"No implementation or factory for {interface.__name__}")

        return errors

    def get_statistics(self) -> dict[str, Any]:
        """Get container statistics."""
        return {
            "total_registrations": len(self._registrations),
            "singleton_instances": len(self._singletons),
            "request_scope_instances": len(self._request_scope),
            "initialized": self._initialized,
        }

    def cleanup(self) -> None:
        """Clean up container resources."""
        self._singletons.clear()
        self._request_scope.clear()
        self._initialized = False
        logger.info("🧹 Cleaned up DI container")
