"""
Test utilities for service discovery testing.

Provides helper functions and utilities to make service discovery testing
more convenient and consistent across test suites.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Callable
from unittest.mock import Mock, AsyncMock

try:
    from kickai.core.service_discovery import (
        ServiceRegistry,
        ServiceDefinition,
        ServiceType,
        ServiceConfiguration,
        ServiceHealth,
        ServiceStatus,
        DependencyContainerServiceDiscovery,
        register_default_health_checkers,
    )
except ImportError:
    # Graceful handling if service discovery is not available
    ServiceRegistry = None
    ServiceDefinition = None
    ServiceType = None
    ServiceConfiguration = None
    ServiceHealth = None
    ServiceStatus = None
    DependencyContainerServiceDiscovery = None
    register_default_health_checkers = lambda x: None


class ServiceTestBuilder:
    """Builder pattern for creating test services and configurations."""
    
    def __init__(self):
        self.services = {}
        self.definitions = []
        self.health_checkers = []
        self.config = None
    
    def with_service(self, name: str, service_type: ServiceType, 
                    dependencies: List[str] = None, **kwargs) -> 'ServiceTestBuilder':
        """Add a service to the test setup."""
        if ServiceDefinition is None:
            return self
        
        dependencies = dependencies or []
        
        # Create service definition
        definition = ServiceDefinition(
            name=name,
            service_type=service_type,
            dependencies=dependencies,
            **kwargs
        )
        self.definitions.append(definition)
        
        # Create mock service instance
        service = create_mock_service(name, service_type)
        self.services[name] = service
        
        return self
    
    def with_config(self, **config_kwargs) -> 'ServiceTestBuilder':
        """Set service configuration."""
        if ServiceConfiguration is None:
            return self
        
        self.config = ServiceConfiguration(**config_kwargs)
        return self
    
    def with_health_checker(self, checker) -> 'ServiceTestBuilder':
        """Add a health checker."""
        self.health_checkers.append(checker)
        return self
    
    def build_registry(self) -> Optional[ServiceRegistry]:
        """Build and populate a service registry."""
        if ServiceRegistry is None:
            return None
        
        # Use default config if none provided
        config = self.config or ServiceConfiguration()
        registry = ServiceRegistry(config)
        
        # Register services
        for definition in self.definitions:
            service_instance = self.services.get(definition.name)
            registry.register_service(definition, service_instance)
        
        # Add health checkers
        for checker in self.health_checkers:
            registry.add_health_checker(checker)
        
        # Add default health checkers if none were provided
        if not self.health_checkers:
            register_default_health_checkers(registry)
        
        return registry
    
    def get_services(self) -> Dict[str, Any]:
        """Get all service instances."""
        return self.services.copy()
    
    def get_definitions(self) -> List[ServiceDefinition]:
        """Get all service definitions."""
        return self.definitions.copy()


def create_mock_service(name: str, service_type: ServiceType, **kwargs) -> Mock:
    """Create a mock service with appropriate methods based on service type."""
    service = Mock()
    service.name = name
    service.service_type = service_type.value if service_type else "unknown"
    
    # Add common methods
    service.health_check = AsyncMock(return_value=True)
    
    # Add type-specific methods
    if service_type == ServiceType.CORE:
        if "database" in name.lower() or "store" in name.lower():
            # Database-like service
            service.ping = AsyncMock(return_value=True)
            service.test_connection = AsyncMock(return_value=True)
            service.create_document = AsyncMock(return_value={"id": "doc_123"})
            service.get_document = AsyncMock(return_value={"id": "doc_123"})
            service.update_document = AsyncMock(return_value={"id": "doc_123"})
        elif "agent" in name.lower() or "factory" in name.lower():
            # Agent-like service
            service.create_agent = Mock(return_value=Mock(name="TestAgent"))
            service.get_agents = Mock(return_value=[])
    
    elif service_type == ServiceType.FEATURE:
        if "player" in name.lower():
            # Player service methods
            service.get_player = AsyncMock(return_value={"id": "player_123"})
            service.create_player = AsyncMock(return_value={"id": "player_123"})
            service.update_player = AsyncMock(return_value={"id": "player_123"})
        elif "team" in name.lower():
            # Team service methods
            service.get_team = AsyncMock(return_value={"id": "team_123"})
            service.create_team = AsyncMock(return_value={"id": "team_123"})
            service.update_team = AsyncMock(return_value={"id": "team_123"})
        elif "match" in name.lower():
            # Match service methods
            service.get_match = AsyncMock(return_value={"id": "match_123"})
            service.create_match = AsyncMock(return_value={"id": "match_123"})
            service.update_match = AsyncMock(return_value={"id": "match_123"})
    
    elif service_type == ServiceType.EXTERNAL:
        # External service methods
        service.test_connection = AsyncMock(return_value=True)
        service.ping = AsyncMock(return_value=True)
        
        if "telegram" in name.lower() or "bot" in name.lower():
            service.send_message = AsyncMock(return_value={"message_id": "msg_123"})
        elif "firebase" in name.lower():
            service.get_document = AsyncMock(return_value={"id": "doc_123"})
            service.set_document = AsyncMock(return_value=True)
    
    # Apply any custom kwargs
    for key, value in kwargs.items():
        setattr(service, key, value)
    
    return service


def create_failing_service(name: str, service_type: ServiceType, 
                          failure_message: str = "Service failure") -> Mock:
    """Create a mock service that always fails health checks."""
    service = create_mock_service(name, service_type)
    
    # Override health check to fail
    async def failing_health_check():
        raise Exception(failure_message)
    
    service.health_check = failing_health_check
    
    # Also make connection-related methods fail for external services
    if service_type == ServiceType.EXTERNAL:
        service.test_connection = AsyncMock(side_effect=Exception(failure_message))
        service.ping = AsyncMock(side_effect=Exception(failure_message))
    
    return service


def create_slow_service(name: str, service_type: ServiceType, 
                       delay: float = 1.0) -> Mock:
    """Create a mock service with slow health checks."""
    service = create_mock_service(name, service_type)
    
    # Override health check to be slow
    async def slow_health_check():
        await asyncio.sleep(delay)
        return True
    
    service.health_check = slow_health_check
    
    return service


class MockDependencyContainer:
    """Mock dependency container for testing service discovery."""
    
    def __init__(self):
        self._services = {}
        self._singletons = {}
    
    def add_service(self, name: str, service_type: ServiceType, **kwargs):
        """Add a service to the container."""
        service_info = Mock()
        service_info.interface = f"test.I{name}"
        service_info.implementation = f"test.{name}Impl"
        
        self._services[name] = service_info
        return self
    
    def add_singleton(self, name: str, instance):
        """Add a singleton to the container."""
        self._singletons[name] = instance
        return self
    
    def get_service(self, name: str):
        """Get service instance (mock)."""
        if name in self._services:
            return Mock(name=f"MockInstance_{name}")
        return None
    
    def get_singleton(self, name: str):
        """Get singleton instance."""
        return self._singletons.get(name)


async def wait_for_health_status(registry: ServiceRegistry, service_name: str, 
                                expected_status: ServiceStatus, 
                                timeout: float = 5.0, 
                                check_interval: float = 0.1) -> bool:
    """Wait for a service to reach a specific health status."""
    if ServiceStatus is None:
        return False
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            health = await registry.check_service_health(service_name)
            if health.status == expected_status:
                return True
        except Exception:
            pass  # Continue waiting
        
        await asyncio.sleep(check_interval)
    
    return False


async def wait_for_all_healthy(registry: ServiceRegistry, 
                              service_names: List[str] = None,
                              timeout: float = 10.0) -> Dict[str, bool]:
    """Wait for all specified services (or all services) to become healthy."""
    if ServiceStatus is None:
        return {}
    
    if service_names is None:
        service_names = registry.list_services()
    
    results = {}
    tasks = []
    
    for service_name in service_names:
        task = wait_for_health_status(registry, service_name, ServiceStatus.HEALTHY, timeout)
        tasks.append((service_name, task))
    
    # Wait for all tasks to complete
    for service_name, task in tasks:
        results[service_name] = await task
    
    return results


def assert_service_healthy(health: ServiceHealth, 
                          expected_response_time_max: float = None):
    """Assert that a service health check result indicates a healthy service."""
    if ServiceStatus is None:
        return
    
    assert health.status == ServiceStatus.HEALTHY, f"Service {health.service_name} is not healthy: {health.error_message}"
    assert health.error_message is None, f"Healthy service should not have error message: {health.error_message}"
    assert health.last_check is not None, "Health check should have timestamp"
    
    if expected_response_time_max is not None and health.response_time is not None:
        assert health.response_time <= expected_response_time_max, f"Response time {health.response_time} exceeds maximum {expected_response_time_max}"


def assert_service_unhealthy(health: ServiceHealth, 
                            expected_error_substring: str = None):
    """Assert that a service health check result indicates an unhealthy service."""
    if ServiceStatus is None:
        return
    
    assert health.status == ServiceStatus.UNHEALTHY, f"Service {health.service_name} should be unhealthy but is {health.status.value}"
    assert health.error_message is not None, "Unhealthy service should have error message"
    
    if expected_error_substring:
        assert expected_error_substring.lower() in health.error_message.lower(), f"Error message '{health.error_message}' should contain '{expected_error_substring}'"


def create_realistic_service_topology() -> Dict[str, Any]:
    """Create a realistic service topology for testing."""
    if ServiceType is None:
        return {"services": {}, "definitions": []}
    
    builder = ServiceTestBuilder()
    
    # Core services (no dependencies)
    builder.with_service("DataStoreInterface", ServiceType.CORE, [], timeout=5.0)
    builder.with_service("DependencyContainer", ServiceType.CORE, [], timeout=3.0)
    
    # External services
    builder.with_service("FirebaseClient", ServiceType.EXTERNAL, [], timeout=10.0)
    builder.with_service("TelegramBot", ServiceType.EXTERNAL, [], timeout=15.0)
    
    # Feature services (depend on core and external)
    builder.with_service("PlayerService", ServiceType.FEATURE, ["DataStoreInterface"], timeout=8.0)
    builder.with_service("TeamService", ServiceType.FEATURE, ["DataStoreInterface", "PlayerService"], timeout=8.0)
    builder.with_service("MatchService", ServiceType.FEATURE, ["DataStoreInterface", "PlayerService", "TeamService"], timeout=12.0)
    
    # Agent services
    builder.with_service("AgentFactory", ServiceType.CORE, ["DependencyContainer"], timeout=6.0)
    builder.with_service("MessageRouter", ServiceType.CORE, ["AgentFactory", "PlayerService", "TeamService"], timeout=10.0)
    
    # Utility services
    builder.with_service("NotificationService", ServiceType.UTILITY, ["TelegramBot"], timeout=5.0)
    
    return {
        "services": builder.get_services(),
        "definitions": builder.get_definitions(),
        "builder": builder
    }


class HealthCheckRecorder:
    """Records health check calls for analysis."""
    
    def __init__(self):
        self.calls = []
        self.call_count = 0
    
    async def record_health_check(self, service_name: str, service_instance: Any) -> ServiceHealth:
        """Record a health check call."""
        call_info = {
            "timestamp": time.time(),
            "service_name": service_name,
            "call_number": self.call_count
        }
        self.calls.append(call_info)
        self.call_count += 1
        
        # Delegate to actual health check if service has one
        if hasattr(service_instance, 'health_check'):
            try:
                result = await service_instance.health_check()
                return ServiceHealth(
                    service_name=service_name,
                    status=ServiceStatus.HEALTHY if result else ServiceStatus.UNHEALTHY,
                    last_check=time.time(),
                    response_time=0.1,
                    metadata={"recorded": True, "call_number": self.call_count - 1}
                )
            except Exception as e:
                return ServiceHealth(
                    service_name=service_name,
                    status=ServiceStatus.UNHEALTHY,
                    last_check=time.time(),
                    error_message=str(e),
                    metadata={"recorded": True, "call_number": self.call_count - 1}
                )
        
        # Default healthy response
        return ServiceHealth(
            service_name=service_name,
            status=ServiceStatus.HEALTHY,
            last_check=time.time(),
            response_time=0.1,
            metadata={"recorded": True, "call_number": self.call_count - 1}
        )
    
    def supports_service(self, service_name: str) -> bool:
        """Support all services for recording."""
        return True
    
    def get_calls_for_service(self, service_name: str) -> List[Dict[str, Any]]:
        """Get all recorded calls for a specific service."""
        return [call for call in self.calls if call["service_name"] == service_name]
    
    def get_call_count_for_service(self, service_name: str) -> int:
        """Get the number of health check calls for a service."""
        return len(self.get_calls_for_service(service_name))
    
    def reset(self):
        """Reset all recorded calls."""
        self.calls = []
        self.call_count = 0


# Convenience functions for common test scenarios
def create_basic_test_registry() -> Optional[ServiceRegistry]:
    """Create a basic test registry with common services."""
    if ServiceType is None:
        return None
    
    return (ServiceTestBuilder()
            .with_service("DataStore", ServiceType.CORE)
            .with_service("PlayerService", ServiceType.FEATURE, ["DataStore"])
            .with_service("TelegramBot", ServiceType.EXTERNAL)
            .with_config(health_check_enabled=True, circuit_breaker_enabled=True)
            .build_registry())


def create_failing_services_registry() -> Optional[ServiceRegistry]:
    """Create a registry with some failing services for failure testing."""
    if ServiceType is None:
        return None
    
    builder = ServiceTestBuilder()
    builder.with_service("HealthyService", ServiceType.CORE)
    builder.with_config(health_check_enabled=True, circuit_breaker_enabled=True)
    
    # Build registry and replace one service with failing version
    registry = builder.build_registry()
    
    # Add a failing service manually
    failing_service = create_failing_service("FailingService", ServiceType.FEATURE)
    failing_definition = ServiceDefinition("FailingService", ServiceType.FEATURE)
    registry.register_service(failing_definition, failing_service)
    
    return registry


def create_performance_test_registry(service_count: int = 50) -> Optional[ServiceRegistry]:
    """Create a registry with many services for performance testing."""
    if ServiceType is None:
        return None
    
    builder = ServiceTestBuilder()
    builder.with_config(health_check_enabled=True, circuit_breaker_enabled=True)
    
    # Add many services
    for i in range(service_count):
        service_type = [ServiceType.CORE, ServiceType.FEATURE, ServiceType.EXTERNAL, ServiceType.UTILITY][i % 4]
        builder.with_service(f"Service{i}", service_type)
    
    return builder.build_registry()
