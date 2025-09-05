"""
Dynamic Service Registry Implementation

Thread-safe, high-performance service registry with circuit breaker pattern,
health monitoring, and automatic service discovery capabilities.
"""

import asyncio
import logging
import threading
import time
from collections import defaultdict
from typing import Any

from .interfaces import (
    CircuitBreakerOpenError,
    IServiceHealthChecker,
    IServiceRegistry,
    ServiceConfiguration,
    ServiceDefinition,
    ServiceHealth,
    ServiceNotFoundError,
    ServiceRegistrationError,
    ServiceStatus,
    ServiceType,
)

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker implementation for service health management."""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self._lock = threading.Lock()

    def can_execute(self) -> bool:
        """Check if operation can be executed based on circuit breaker state."""
        with self._lock:
            current_time = time.time()

            if self.state == "CLOSED":
                return True
            elif self.state == "OPEN":
                if current_time - self.last_failure_time >= self.timeout:
                    self.state = "HALF_OPEN"
                    return True
                return False
            else:  # HALF_OPEN
                return True

    def record_success(self):
        """Record a successful operation."""
        with self._lock:
            self.failure_count = 0
            self.state = "CLOSED"

    def record_failure(self):
        """Record a failed operation."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"


class DefaultServiceHealthChecker:
    """Default health checker implementation."""

    async def check_health(self, service_name: str, service_instance: Any) -> ServiceHealth:
        """Default health check - checks if service instance exists and has basic methods."""
        try:
            start_time = time.time()

            # Basic existence check
            if service_instance is None:
                return ServiceHealth(
                    service_name=service_name,
                    status=ServiceStatus.UNHEALTHY,
                    last_check=time.time(),
                    error_message="Service instance is None",
                )

            # Check if service has a health check method
            if hasattr(service_instance, "health_check"):
                try:
                    health_result = await service_instance.health_check()
                    response_time = time.time() - start_time

                    return ServiceHealth(
                        service_name=service_name,
                        status=ServiceStatus.HEALTHY if health_result else ServiceStatus.UNHEALTHY,
                        last_check=time.time(),
                        response_time=response_time,
                        metadata={"has_health_check": True},
                    )
                except Exception as e:
                    response_time = time.time() - start_time
                    return ServiceHealth(
                        service_name=service_name,
                        status=ServiceStatus.UNHEALTHY,
                        last_check=time.time(),
                        response_time=response_time,
                        error_message=str(e),
                        metadata={"has_health_check": True, "health_check_failed": True},
                    )

            # Basic instance check - service exists
            response_time = time.time() - start_time
            return ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.HEALTHY,
                last_check=time.time(),
                response_time=response_time,
                metadata={"basic_check": True},
            )

        except Exception as e:
            return ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.UNHEALTHY,
                last_check=time.time(),
                error_message=str(e),
            )

    def supports_service(self, service_name: str) -> bool:
        """Default checker supports all services."""
        return True


class ServiceRegistry(IServiceRegistry):
    """Thread-safe service registry with health monitoring and circuit breaker."""

    def __init__(self, config: ServiceConfiguration = None):
        self.config = config or ServiceConfiguration()
        self._services: dict[str, Any] = {}
        self._definitions: dict[str, ServiceDefinition] = {}
        self._health_status: dict[str, ServiceHealth] = {}
        self._circuit_breakers: dict[str, CircuitBreaker] = {}
        self._health_checkers: list[IServiceHealthChecker] = []
        self._lock = threading.RLock()
        self._health_check_tasks: dict[str, asyncio.Task] = {}
        self._running = False

        # Add default health checker
        self._health_checkers.append(DefaultServiceHealthChecker())

    def register_service(self, definition: ServiceDefinition, instance: Any = None) -> None:
        """Register a service with its definition and optional instance."""
        try:
            with self._lock:
                if definition.name in self._services:
                    logger.warning(f"Service {definition.name} already registered, updating...")

                self._definitions[definition.name] = definition

                if instance is not None:
                    self._services[definition.name] = instance

                # Initialize circuit breaker if enabled
                if self.config.circuit_breaker_enabled:
                    self._circuit_breakers[definition.name] = CircuitBreaker(
                        failure_threshold=self.config.circuit_breaker_threshold,
                        timeout=self.config.circuit_breaker_timeout,
                    )

                # Initialize health status
                self._health_status[definition.name] = ServiceHealth(
                    service_name=definition.name, status=ServiceStatus.UNKNOWN
                )

                logger.info(f"✅ Service {definition.name} registered successfully")

        except Exception as e:
            logger.error(f"❌ Failed to register service {definition.name}: {e}")
            raise ServiceRegistrationError(f"Failed to register service {definition.name}: {e}")

    def unregister_service(self, service_name: str) -> None:
        """Unregister a service."""
        with self._lock:
            # Cancel health check task if running
            if service_name in self._health_check_tasks:
                task = self._health_check_tasks[service_name]
                if not task.done():
                    task.cancel()
                del self._health_check_tasks[service_name]

            # Remove from all registries
            self._services.pop(service_name, None)
            self._definitions.pop(service_name, None)
            self._health_status.pop(service_name, None)
            self._circuit_breakers.pop(service_name, None)

            logger.info(f"🗑️ Service {service_name} unregistered")

    def get_service(self, service_name: str) -> Any | None:
        """Get a service instance by name."""
        with self._lock:
            return self._services.get(service_name)

    def get_service_definition(self, service_name: str) -> ServiceDefinition | None:
        """Get service definition by name."""
        with self._lock:
            return self._definitions.get(service_name)

    def list_services(self, service_type: ServiceType | None = None) -> list[str]:
        """List all registered services, optionally filtered by type."""
        with self._lock:
            if service_type is None:
                return list(self._definitions.keys())

            return [
                name
                for name, definition in self._definitions.items()
                if definition.service_type == service_type
            ]

    def get_services_by_type(self, service_type: ServiceType) -> dict[str, Any]:
        """Get all services of a specific type."""
        with self._lock:
            result = {}
            for name, definition in self._definitions.items():
                if definition.service_type == service_type:
                    instance = self._services.get(name)
                    if instance is not None:
                        result[name] = instance
            return result

    async def check_service_health(self, service_name: str) -> ServiceHealth:
        """Check the health of a specific service."""
        definition = self.get_service_definition(service_name)
        if not definition:
            raise ServiceNotFoundError(f"Service {service_name} not found")

        # Check circuit breaker
        if self.config.circuit_breaker_enabled:
            circuit_breaker = self._circuit_breakers.get(service_name)
            if circuit_breaker and not circuit_breaker.can_execute():
                raise CircuitBreakerOpenError(f"Circuit breaker open for service {service_name}")

        instance = self.get_service(service_name)

        # Find appropriate health checker
        health_checker = None
        for checker in self._health_checkers:
            if checker.supports_service(service_name):
                health_checker = checker
                break

        if not health_checker:
            return ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.UNKNOWN,
                last_check=time.time(),
                error_message="No health checker available",
            )

        try:
            health = await asyncio.wait_for(
                health_checker.check_health(service_name, instance), timeout=definition.timeout
            )

            # Update circuit breaker
            if self.config.circuit_breaker_enabled:
                circuit_breaker = self._circuit_breakers.get(service_name)
                if circuit_breaker:
                    if health.status == ServiceStatus.HEALTHY:
                        circuit_breaker.record_success()
                    else:
                        circuit_breaker.record_failure()

            # Cache health status
            with self._lock:
                self._health_status[service_name] = health

            return health

        except TimeoutError:
            health = ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.UNHEALTHY,
                last_check=time.time(),
                error_message=f"Health check timeout after {definition.timeout}s",
            )

            # Record failure in circuit breaker
            if self.config.circuit_breaker_enabled:
                circuit_breaker = self._circuit_breakers.get(service_name)
                if circuit_breaker:
                    circuit_breaker.record_failure()

            with self._lock:
                self._health_status[service_name] = health

            return health

        except Exception as e:
            logger.error(f"❌ Health check failed for {service_name}: {e}")
            health = ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.UNHEALTHY,
                last_check=time.time(),
                error_message=str(e),
            )

            # Record failure in circuit breaker
            if self.config.circuit_breaker_enabled:
                circuit_breaker = self._circuit_breakers.get(service_name)
                if circuit_breaker:
                    circuit_breaker.record_failure()

            with self._lock:
                self._health_status[service_name] = health

            return health

    async def check_all_services_health(self) -> dict[str, ServiceHealth]:
        """Check health of all registered services."""
        service_names = self.list_services()

        # Use asyncio.gather for concurrent health checks
        health_checks = [self.check_service_health(service_name) for service_name in service_names]

        try:
            health_results = await asyncio.gather(*health_checks, return_exceptions=True)

            result = {}
            for service_name, health in zip(service_names, health_results, strict=False):
                if isinstance(health, Exception):
                    result[service_name] = ServiceHealth(
                        service_name=service_name,
                        status=ServiceStatus.UNHEALTHY,
                        last_check=time.time(),
                        error_message=str(health),
                    )
                else:
                    result[service_name] = health

            return result

        except Exception as e:
            logger.error(f"❌ Bulk health check failed: {e}")
            # Return cached status for all services
            with self._lock:
                return dict(self._health_status)

    def is_service_healthy(self, service_name: str) -> bool:
        """Quick check if a service is healthy based on cached status."""
        with self._lock:
            health = self._health_status.get(service_name)
            return health is not None and health.status == ServiceStatus.HEALTHY

    def add_health_checker(self, health_checker: IServiceHealthChecker) -> None:
        """Add a custom health checker."""
        self._health_checkers.insert(0, health_checker)  # Custom checkers have priority
        logger.info("✅ Added custom health checker")

    def get_service_statistics(self) -> dict[str, Any]:
        """Get service registry statistics."""
        with self._lock:
            stats = {
                "total_services": len(self._definitions),
                "services_by_type": defaultdict(int),
                "health_status_distribution": defaultdict(int),
                "circuit_breaker_states": defaultdict(int),
            }

            for definition in self._definitions.values():
                stats["services_by_type"][definition.service_type.value] += 1

            for health in self._health_status.values():
                stats["health_status_distribution"][health.status.value] += 1

            for circuit_breaker in self._circuit_breakers.values():
                stats["circuit_breaker_states"][circuit_breaker.state] += 1

            return dict(stats)


# Global registry instance
_global_registry: ServiceRegistry | None = None
_registry_lock = threading.Lock()


def get_service_registry(config: ServiceConfiguration = None) -> ServiceRegistry:
    """Get the global service registry instance."""
    global _global_registry

    if _global_registry is None:
        with _registry_lock:
            if _global_registry is None:
                _global_registry = ServiceRegistry(config)

    return _global_registry


def reset_service_registry() -> None:
    """Reset the global service registry (primarily for testing)."""
    global _global_registry

    with _registry_lock:
        if _global_registry:
            # Cleanup any running tasks
            for task in _global_registry._health_check_tasks.values():
                if not task.done():
                    task.cancel()

        _global_registry = None
