"""
Dynamic Service Discovery Package

Provides dynamic service discovery capabilities to reduce tight coupling
in system validation and enable runtime service registration and health checking.
"""

from .discovery import (
    CompositeServiceDiscovery,
    DependencyContainerServiceDiscovery,
    ModuleServiceDiscovery,
    create_service_discovery_from_config,
    get_service_discovery,
)
from .health_checkers import (
    AgentServiceHealthChecker,
    DatabaseServiceHealthChecker,
    ExternalServiceHealthChecker,
    PlayerServiceHealthChecker,
    TeamServiceHealthChecker,
    get_default_health_checkers,
    register_default_health_checkers,
)
from .interfaces import (
    CircuitBreakerOpenError,
    IServiceDiscovery,
    IServiceHealthChecker,
    IServiceRegistry,
    ServiceConfiguration,
    ServiceDefinition,
    ServiceDiscoveryError,
    ServiceHealth,
    ServiceHealthCheckError,
    ServiceNotFoundError,
    ServiceRegistrationError,
    ServiceStatus,
    ServiceType,
)
from .registry import (
    ServiceRegistry,
    get_service_registry,
    reset_service_registry,
)

__all__ = [
    # Interfaces
    "IServiceRegistry",
    "IServiceDiscovery",
    "IServiceHealthChecker",
    "ServiceDefinition",
    "ServiceHealth",
    "ServiceStatus",
    "ServiceType",
    "ServiceConfiguration",
    "ServiceDiscoveryError",
    "ServiceRegistrationError",
    "ServiceHealthCheckError",
    "ServiceNotFoundError",
    "CircuitBreakerOpenError",
    # Registry
    "ServiceRegistry",
    "get_service_registry",
    "reset_service_registry",
    # Discovery
    "DependencyContainerServiceDiscovery",
    "ModuleServiceDiscovery",
    "CompositeServiceDiscovery",
    "get_service_discovery",
    "create_service_discovery_from_config",
    # Health Checkers
    "DatabaseServiceHealthChecker",
    "PlayerServiceHealthChecker",
    "TeamServiceHealthChecker",
    "AgentServiceHealthChecker",
    "ExternalServiceHealthChecker",
    "get_default_health_checkers",
    "register_default_health_checkers",
]
