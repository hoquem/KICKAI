"""
Dynamic Service Discovery Package

Provides dynamic service discovery capabilities to reduce tight coupling
in system validation and enable runtime service registration and health checking.
"""

from .interfaces import (
    IServiceRegistry,
    IServiceDiscovery,
    IServiceHealthChecker,
    ServiceDefinition,
    ServiceHealth,
    ServiceStatus,
    ServiceType,
    ServiceConfiguration,
    ServiceDiscoveryError,
    ServiceRegistrationError,
    ServiceHealthCheckError,
    ServiceNotFoundError,
    CircuitBreakerOpenError,
)

from .registry import (
    ServiceRegistry,
    get_service_registry,
    reset_service_registry,
)

from .discovery import (
    DependencyContainerServiceDiscovery,
    ModuleServiceDiscovery,
    CompositeServiceDiscovery,
    get_service_discovery,
    create_service_discovery_from_config,
)

from .health_checkers import (
    DatabaseServiceHealthChecker,
    PlayerServiceHealthChecker,
    TeamServiceHealthChecker,
    AgentServiceHealthChecker,
    ExternalServiceHealthChecker,
    get_default_health_checkers,
    register_default_health_checkers,
)

__all__ = [
    # Interfaces
    'IServiceRegistry',
    'IServiceDiscovery', 
    'IServiceHealthChecker',
    'ServiceDefinition',
    'ServiceHealth',
    'ServiceStatus',
    'ServiceType',
    'ServiceConfiguration',
    'ServiceDiscoveryError',
    'ServiceRegistrationError',
    'ServiceHealthCheckError',
    'ServiceNotFoundError',
    'CircuitBreakerOpenError',
    
    # Registry
    'ServiceRegistry',
    'get_service_registry',
    'reset_service_registry',
    
    # Discovery
    'DependencyContainerServiceDiscovery',
    'ModuleServiceDiscovery',
    'CompositeServiceDiscovery',
    'get_service_discovery',
    'create_service_discovery_from_config',
    
    # Health Checkers
    'DatabaseServiceHealthChecker',
    'PlayerServiceHealthChecker',
    'TeamServiceHealthChecker',
    'AgentServiceHealthChecker',
    'ExternalServiceHealthChecker',
    'get_default_health_checkers',
    'register_default_health_checkers',
]