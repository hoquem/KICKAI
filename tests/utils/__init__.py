"""
Test utilities package.

Provides common utilities and helpers for testing across the KICKAI project.
"""

try:
    from .service_discovery_utils import (
        ServiceTestBuilder,
        create_mock_service,
        create_failing_service,
        create_slow_service,
        MockDependencyContainer,
        wait_for_health_status,
        wait_for_all_healthy,
        assert_service_healthy,
        assert_service_unhealthy,
        create_realistic_service_topology,
        HealthCheckRecorder,
        create_basic_test_registry,
        create_failing_services_registry,
        create_performance_test_registry,
    )
except ImportError:
    # Service discovery utilities not available
    pass

__all__ = [
    # Service Discovery Utils (if available)
    'ServiceTestBuilder',
    'create_mock_service',
    'create_failing_service', 
    'create_slow_service',
    'MockDependencyContainer',
    'wait_for_health_status',
    'wait_for_all_healthy',
    'assert_service_healthy',
    'assert_service_unhealthy',
    'create_realistic_service_topology',
    'HealthCheckRecorder',
    'create_basic_test_registry',
    'create_failing_services_registry',
    'create_performance_test_registry',
]
