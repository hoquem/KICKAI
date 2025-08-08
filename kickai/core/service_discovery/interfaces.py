"""
Service Discovery Interfaces

Dynamic service discovery system to reduce tight coupling in system validation
and enable runtime service registration and health checking.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, TypeVar


class ServiceStatus(Enum):
    """Service health status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    DISABLED = "disabled"


class ServiceType(Enum):
    """Service type classification."""
    CORE = "core"          # Critical services required for startup
    FEATURE = "feature"    # Feature-specific services
    EXTERNAL = "external"  # External service integrations
    UTILITY = "utility"    # Utility services


@dataclass
class ServiceDefinition:
    """Service definition with metadata and configuration."""
    name: str
    service_type: ServiceType
    interface_name: Optional[str] = None
    implementation_class: Optional[str] = None
    dependencies: List[str] = None
    health_check_enabled: bool = True
    health_check_interval: int = 60  # seconds
    timeout: float = 30.0
    retry_count: int = 3
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ServiceHealth:
    """Service health status information."""
    service_name: str
    status: ServiceStatus
    last_check: Optional[float] = None
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class IServiceHealthChecker(Protocol):
    """Protocol for service health checking."""

    async def check_health(self, service_name: str, service_instance: Any) -> ServiceHealth:
        """Check the health of a specific service."""
        ...

    def supports_service(self, service_name: str) -> bool:
        """Check if this health checker supports the given service."""
        ...


class IServiceRegistry(ABC):
    """Abstract interface for service registry."""

    @abstractmethod
    def register_service(self, definition: ServiceDefinition, instance: Any = None) -> None:
        """Register a service with its definition and optional instance."""
        pass

    @abstractmethod
    def unregister_service(self, service_name: str) -> None:
        """Unregister a service."""
        pass

    @abstractmethod
    def get_service(self, service_name: str) -> Optional[Any]:
        """Get a service instance by name."""
        pass

    @abstractmethod
    def get_service_definition(self, service_name: str) -> Optional[ServiceDefinition]:
        """Get service definition by name."""
        pass

    @abstractmethod
    def list_services(self, service_type: Optional[ServiceType] = None) -> List[str]:
        """List all registered services, optionally filtered by type."""
        pass

    @abstractmethod
    def get_services_by_type(self, service_type: ServiceType) -> Dict[str, Any]:
        """Get all services of a specific type."""
        pass

    @abstractmethod
    async def check_service_health(self, service_name: str) -> ServiceHealth:
        """Check the health of a specific service."""
        pass

    @abstractmethod
    async def check_all_services_health(self) -> Dict[str, ServiceHealth]:
        """Check health of all registered services."""
        pass

    @abstractmethod
    def is_service_healthy(self, service_name: str) -> bool:
        """Quick check if a service is healthy."""
        pass


class IServiceDiscovery(ABC):
    """Abstract interface for service discovery system."""

    @abstractmethod
    def discover_services(self) -> List[ServiceDefinition]:
        """Discover available services."""
        pass

    @abstractmethod
    def auto_register_services(self, registry: IServiceRegistry) -> None:
        """Auto-register discovered services with the registry."""
        pass

    @abstractmethod
    def can_discover_service(self, service_name: str) -> bool:
        """Check if a service can be discovered."""
        pass


T = TypeVar('T')


class ServiceFactory(Protocol[T]):
    """Protocol for service factory."""

    def create_service(self, service_name: str, **kwargs) -> Optional[T]:
        """Create a service instance."""
        ...

    def supports_service(self, service_name: str) -> bool:
        """Check if factory can create the service."""
        ...


@dataclass
class ServiceConfiguration:
    """Configuration for service discovery system."""
    auto_discovery_enabled: bool = True
    health_check_enabled: bool = True
    health_check_interval: int = 60
    service_timeout: float = 30.0
    retry_attempts: int = 3
    circuit_breaker_enabled: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60

    # Service type priorities for startup validation
    startup_service_types: List[ServiceType] = None

    def __post_init__(self):
        if self.startup_service_types is None:
            self.startup_service_types = [
                ServiceType.CORE,
                ServiceType.FEATURE,
                ServiceType.EXTERNAL,
                ServiceType.UTILITY
            ]


class ServiceDiscoveryError(Exception):
    """Base exception for service discovery errors."""
    pass


class ServiceRegistrationError(ServiceDiscoveryError):
    """Exception raised when service registration fails."""
    pass


class ServiceHealthCheckError(ServiceDiscoveryError):
    """Exception raised when service health check fails."""
    pass


class ServiceNotFoundError(ServiceDiscoveryError):
    """Exception raised when a required service is not found."""
    pass


class CircuitBreakerOpenError(ServiceDiscoveryError):
    """Exception raised when circuit breaker is open for a service."""
    pass
