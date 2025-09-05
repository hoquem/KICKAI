"""
Dynamic Service Discovery Implementation

Automatic service discovery system that reduces tight coupling by
dynamically discovering and registering services at runtime.
"""

import importlib
import inspect
import logging
import pkgutil
from typing import Any

from kickai.core.dependency_container import DependencyContainer, get_container

from .interfaces import (
    IServiceDiscovery,
    IServiceRegistry,
    ServiceDefinition,
    ServiceDiscoveryError,
    ServiceType,
)

logger = logging.getLogger(__name__)


class DependencyContainerServiceDiscovery(IServiceDiscovery):
    """Service discovery using the existing dependency container."""

    def __init__(self, container: DependencyContainer | None = None):
        self.container = container or get_container()

    def discover_services(self) -> list[ServiceDefinition]:
        """Discover services from the dependency container."""
        discovered_services = []

        try:
            # Get all registered services from the container
            if hasattr(self.container, "_services") and self.container._services:
                for service_name, service_info in self.container._services.items():
                    service_type = self._classify_service_type(service_name)

                    definition = ServiceDefinition(
                        name=service_name,
                        service_type=service_type,
                        interface_name=getattr(service_info, "interface", None),
                        implementation_class=getattr(service_info, "implementation", None),
                        metadata={
                            "discovery_method": "dependency_container",
                            "container_type": type(self.container).__name__,
                        },
                    )

                    discovered_services.append(definition)
                    logger.debug(f"✅ Discovered service: {service_name} ({service_type.value})")

            # Get singletons from container
            if hasattr(self.container, "_singletons") and self.container._singletons:
                for singleton_name, singleton_instance in self.container._singletons.items():
                    service_type = self._classify_service_type(singleton_name)

                    definition = ServiceDefinition(
                        name=singleton_name,
                        service_type=service_type,
                        implementation_class=type(singleton_instance).__name__,
                        metadata={
                            "discovery_method": "dependency_container_singleton",
                            "instance_type": type(singleton_instance).__name__,
                        },
                    )

                    discovered_services.append(definition)
                    logger.debug(
                        f"✅ Discovered singleton: {singleton_name} ({service_type.value})"
                    )

            logger.info(
                f"✅ Discovered {len(discovered_services)} services from dependency container"
            )

        except Exception as e:
            logger.error(f"❌ Service discovery from dependency container failed: {e}")
            raise ServiceDiscoveryError(f"Dependency container discovery failed: {e}")

        return discovered_services

    def auto_register_services(self, registry: IServiceRegistry) -> None:
        """Auto-register discovered services with the registry."""
        try:
            discovered_services = self.discover_services()

            for definition in discovered_services:
                # Get the actual service instance
                instance = None

                # Try to get from services first
                if hasattr(self.container, "get_service"):
                    try:
                        instance = self.container.get_service(definition.name)
                    except Exception:
                        pass

                # Try to get from singletons
                if instance is None and hasattr(self.container, "get_singleton"):
                    try:
                        instance = self.container.get_singleton(definition.name)
                    except Exception:
                        pass

                # Register with the service registry
                registry.register_service(definition, instance)

                logger.debug(f"✅ Auto-registered service: {definition.name}")

            logger.info(f"✅ Auto-registered {len(discovered_services)} services")

        except Exception as e:
            logger.error(f"❌ Auto-registration failed: {e}")
            raise ServiceDiscoveryError(f"Auto-registration failed: {e}")

    def can_discover_service(self, service_name: str) -> bool:
        """Check if a service can be discovered."""
        try:
            if hasattr(self.container, "_services") and self.container._services:
                if service_name in self.container._services:
                    return True

            if hasattr(self.container, "_singletons") and self.container._singletons:
                if service_name in self.container._singletons:
                    return True

            return False

        except Exception:
            return False

    def _classify_service_type(self, service_name: str) -> ServiceType:
        """Classify service type based on service name."""
        service_name_lower = service_name.lower()

        # Core services
        if any(
            keyword in service_name_lower
            for keyword in ["datastore", "database", "container", "factory"]
        ):
            return ServiceType.CORE

        # External services
        if any(
            keyword in service_name_lower
            for keyword in ["telegram", "firebase", "llm", "client", "provider"]
        ):
            return ServiceType.EXTERNAL

        # Feature services
        if any(
            keyword in service_name_lower
            for keyword in ["player", "team", "match", "attendance", "payment"]
        ):
            return ServiceType.FEATURE

        # Default to utility
        return ServiceType.UTILITY


class ModuleServiceDiscovery(IServiceDiscovery):
    """Service discovery by scanning Python modules."""

    def __init__(self, package_names: list[str] = None):
        self.package_names = package_names or ["kickai.features", "kickai.core", "kickai.database"]

    def discover_services(self) -> list[ServiceDefinition]:
        """Discover services by scanning modules for service classes."""
        discovered_services = []

        for package_name in self.package_names:
            try:
                discovered_services.extend(self._scan_package(package_name))
            except Exception as e:
                logger.warning(f"⚠️ Failed to scan package {package_name}: {e}")

        logger.info(f"✅ Module discovery found {len(discovered_services)} services")
        return discovered_services

    def _scan_package(self, package_name: str) -> list[ServiceDefinition]:
        """Scan a package for service classes."""
        services = []

        try:
            package = importlib.import_module(package_name)

            for importer, modname, ispkg in pkgutil.iter_modules(
                package.__path__, package.__name__ + "."
            ):
                try:
                    module = importlib.import_module(modname)
                    services.extend(self._scan_module(module))
                except Exception as e:
                    logger.debug(f"⚠️ Failed to scan module {modname}: {e}")

        except Exception as e:
            logger.warning(f"⚠️ Failed to import package {package_name}: {e}")

        return services

    def _scan_module(self, module) -> list[ServiceDefinition]:
        """Scan a module for service classes."""
        services = []

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if self._is_service_class(name, obj):
                service_type = self._classify_service_type(name)

                definition = ServiceDefinition(
                    name=name,
                    service_type=service_type,
                    implementation_class=f"{module.__name__}.{name}",
                    metadata={"discovery_method": "module_scan", "module": module.__name__},
                )

                services.append(definition)
                logger.debug(f"✅ Discovered service class: {name}")

        return services

    def _is_service_class(self, name: str, obj: type) -> bool:
        """Check if a class is a service class."""
        # Skip abstract base classes and test classes
        if name.startswith("Abstract") or name.startswith("Test") or name.startswith("Mock"):
            return False

        # Look for service indicators
        service_indicators = [
            "Service",
            "Repository",
            "Manager",
            "Handler",
            "Controller",
            "Provider",
            "Client",
            "Gateway",
            "Adapter",
        ]

        return any(indicator in name for indicator in service_indicators)

    def _classify_service_type(self, class_name: str) -> ServiceType:
        """Classify service type based on class name."""
        class_name_lower = class_name.lower()

        # Core services
        if any(
            keyword in class_name_lower
            for keyword in ["datastore", "database", "container", "factory", "repository"]
        ):
            return ServiceType.CORE

        # External services
        if any(
            keyword in class_name_lower
            for keyword in ["telegram", "firebase", "llm", "client", "provider"]
        ):
            return ServiceType.EXTERNAL

        # Feature services
        if any(
            keyword in class_name_lower
            for keyword in ["player", "team", "match", "attendance", "payment"]
        ):
            return ServiceType.FEATURE

        # Default to utility
        return ServiceType.UTILITY

    def auto_register_services(self, registry: IServiceRegistry) -> None:
        """Auto-register discovered services (definitions only, no instances)."""
        discovered_services = self.discover_services()

        for definition in discovered_services:
            # Register definition without instance (lazy loading)
            registry.register_service(definition, instance=None)

        logger.info(f"✅ Auto-registered {len(discovered_services)} service definitions")

    def can_discover_service(self, service_name: str) -> bool:
        """Check if a service can be discovered through module scanning."""
        discovered = self.discover_services()
        return any(service.name == service_name for service in discovered)


class CompositeServiceDiscovery(IServiceDiscovery):
    """Composite service discovery that combines multiple discovery methods."""

    def __init__(self, discovery_methods: list[IServiceDiscovery] = None):
        self.discovery_methods = discovery_methods or [
            DependencyContainerServiceDiscovery(),
            ModuleServiceDiscovery(),
        ]

    def discover_services(self) -> list[ServiceDefinition]:
        """Discover services using all available discovery methods."""
        all_discovered = []
        service_names = set()

        for discovery_method in self.discovery_methods:
            try:
                discovered = discovery_method.discover_services()

                # Avoid duplicates based on service name
                for service in discovered:
                    if service.name not in service_names:
                        all_discovered.append(service)
                        service_names.add(service.name)
                    else:
                        logger.debug(f"⚠️ Duplicate service found: {service.name}")

            except Exception as e:
                logger.warning(f"⚠️ Discovery method failed: {e}")

        logger.info(f"✅ Composite discovery found {len(all_discovered)} unique services")
        return all_discovered

    def auto_register_services(self, registry: IServiceRegistry) -> None:
        """Auto-register services using the first successful discovery method."""
        for discovery_method in self.discovery_methods:
            try:
                discovery_method.auto_register_services(registry)
                logger.info(
                    f"✅ Auto-registration successful with {type(discovery_method).__name__}"
                )
                return
            except Exception as e:
                logger.warning(
                    f"⚠️ Auto-registration failed with {type(discovery_method).__name__}: {e}"
                )

        raise ServiceDiscoveryError("All auto-registration methods failed")

    def can_discover_service(self, service_name: str) -> bool:
        """Check if any discovery method can find the service."""
        return any(method.can_discover_service(service_name) for method in self.discovery_methods)


# Global discovery instance
_global_discovery: CompositeServiceDiscovery | None = None


def get_service_discovery() -> CompositeServiceDiscovery:
    """Get the global service discovery instance."""
    global _global_discovery

    if _global_discovery is None:
        _global_discovery = CompositeServiceDiscovery()

    return _global_discovery


def create_service_discovery_from_config(config: dict[str, Any]) -> IServiceDiscovery:
    """Create service discovery from configuration."""
    discovery_type = config.get("type", "composite")

    if discovery_type == "dependency_container":
        return DependencyContainerServiceDiscovery()
    elif discovery_type == "module":
        package_names = config.get("package_names")
        return ModuleServiceDiscovery(package_names)
    elif discovery_type == "composite":
        return CompositeServiceDiscovery()
    else:
        raise ServiceDiscoveryError(f"Unknown discovery type: {discovery_type}")
