# Service Discovery System

## Overview

The KICKAI system includes a comprehensive **Service Discovery System** with dynamic service registration, health monitoring, and circuit breaker patterns. This system provides resilient service management for the 6-agent CrewAI architecture.

## 🏗️ **Architecture**

### Core Components

#### Service Registry (`kickai/core/service_discovery/registry.py`)
- **Central Service Registry**: Thread-safe service registration and discovery
- **Circuit Breaker Integration**: Failure isolation and recovery patterns
- **Health Monitoring**: Continuous service health tracking
- **Service Metadata**: Rich service information and configuration

#### Auto-Discovery (`kickai/core/service_discovery/discovery.py`)
- **Dynamic Discovery**: Automatic service detection and registration
- **Configuration-Driven**: YAML/JSON service definitions
- **Environment-Aware**: Environment-specific service configurations
- **Protocol Support**: HTTP, gRPC, and custom protocol support

#### Health Checkers (`kickai/core/service_discovery/health_checkers.py`)
- **Specialized Checkers**: Service-type specific health validation
- **HTTP Health Checker**: REST endpoint health verification
- **Database Health Checker**: Database connectivity validation
- **Custom Health Checkers**: Extensible health checking framework

#### Configuration System (`kickai/core/service_discovery/config.py`)
- **ServiceConfigurationLoader**: YAML/JSON configuration loading
- **Service Definitions**: Structured service metadata
- **Environment Configuration**: Multi-environment service setup
- **Validation**: Configuration validation and error handling

## 🔧 **Implementation Patterns**

### Service Registration Pattern
```python
from kickai.core.service_discovery.registry import ServiceRegistry
from kickai.core.service_discovery.interfaces import ServiceDefinition

# Register a service
registry = ServiceRegistry()
service_def = ServiceDefinition(
    name="user-service",
    service_type="http",
    url="http://localhost:8001",
    health_check_url="/health",
    metadata={"version": "1.0.0"}
)

service_id = await registry.register_service(service_def)
```

### Service Discovery Pattern
```python
# Discover services
services = await registry.discover_services("user-service")
available_service = registry.get_available_service("user-service")

# Get service with circuit breaker
with registry.get_service_circuit_breaker("user-service") as breaker:
    if breaker.is_closed:
        response = await call_service(available_service)
```

### Health Check Pattern
```python
from kickai.core.service_discovery.health_checkers import HttpHealthChecker

# Custom health checking
health_checker = HttpHealthChecker()
health_result = await health_checker.check_health(service_definition)

if health_result.is_healthy:
    # Service is healthy
    proceed_with_service_call()
else:
    # Handle unhealthy service
    handle_service_failure(health_result.error_message)
```

### Configuration-Driven Setup
```yaml
# config/services.yaml
services:
  api-gateway:
    name: "API Gateway"
    service_type: "http"
    url: "http://localhost:8000"
    health_check_url: "/health"
    timeout: 30
    retry_count: 3
    
  database:
    name: "Main Database"
    service_type: "database"
    connection_string: "postgresql://localhost:5432/kickai"
    health_check_query: "SELECT 1"
```

## 📋 **Development Guidelines**

### Service Definition Standards
1. **Naming Convention**: Use kebab-case for service names (`user-service`, `api-gateway`)
2. **Service Types**: Use standard types (`http`, `database`, `grpc`, `custom`)
3. **Health Check URLs**: Always provide health check endpoints for HTTP services
4. **Metadata**: Include version, environment, and service-specific metadata

### Health Check Implementation
1. **Timeout Configuration**: Set appropriate timeouts for health checks
2. **Retry Logic**: Implement exponential backoff for failed health checks
3. **Error Handling**: Provide detailed error messages for health check failures
4. **Performance**: Keep health checks lightweight and fast

### Circuit Breaker Usage
1. **Failure Thresholds**: Configure appropriate failure thresholds (default: 5 failures)
2. **Recovery Time**: Set reasonable recovery timeouts (default: 60 seconds)
3. **Fallback Strategies**: Implement fallback mechanisms for circuit breaker states
4. **Monitoring**: Log circuit breaker state changes for monitoring

### Configuration Management
1. **Environment Separation**: Use separate configurations for dev/test/prod
2. **Service Discovery**: Support both static and dynamic service configuration
3. **Validation**: Validate all service configurations on startup
4. **Defaults**: Provide sensible defaults for all configuration values

## 🧪 **Testing Strategy**

### Unit Testing
- **Configuration Loading**: Test YAML/JSON configuration parsing
- **Service Registry**: Test service registration and discovery logic
- **Health Checkers**: Test individual health checker implementations
- **Circuit Breaker**: Test circuit breaker state transitions

### Integration Testing
- **Registry-Discovery Integration**: Test complete service discovery workflows
- **Health Check Integration**: Test health checking with real services
- **Circuit Breaker Integration**: Test circuit breaker with service calls
- **Configuration Integration**: Test configuration loading with service setup

### E2E Testing
- **Complete Workflows**: Test end-to-end service discovery scenarios
- **Service Topology**: Test complex service dependency scenarios
- **Failure Recovery**: Test service failure and recovery scenarios
- **Performance**: Test service discovery performance under load

### Test Utilities
```python
from tests.utils.service_discovery_utils import ServiceTestBuilder

# Build test registry with services
registry = (ServiceTestBuilder()
    .add_service("api-gateway", "http://localhost:8000")
    .add_service("user-service", "http://localhost:8001")
    .with_health_checks()
    .with_circuit_breaker()
    .build_registry())
```

## 🚀 **Usage Examples**

### Basic Service Registration
```python
from kickai.core.service_discovery import ServiceRegistry, ServiceDefinition

async def setup_services():
    registry = ServiceRegistry()
    
    # Register API Gateway
    await registry.register_service(ServiceDefinition(
        name="api-gateway",
        service_type="http",
        url="http://localhost:8000",
        health_check_url="/health"
    ))
    
    # Register User Service
    await registry.register_service(ServiceDefinition(
        name="user-service",
        service_type="http", 
        url="http://localhost:8001",
        health_check_url="/health"
    ))
```

### Configuration-Based Setup
```python
from kickai.core.service_discovery.config import ServiceConfigurationLoader

async def load_services_from_config():
    loader = ServiceConfigurationLoader()
    
    # Load from YAML
    services = loader.load_from_yaml("config/services.yaml")
    
    # Load from JSON
    services = loader.load_from_json("config/services.json")
    
    # Register loaded services
    registry = ServiceRegistry()
    for service_def in services:
        await registry.register_service(service_def)
```

### Health Monitoring
```python
from kickai.core.service_discovery.health_checkers import create_health_checker

async def monitor_service_health():
    registry = ServiceRegistry()
    
    for service in registry.get_all_services():
        health_checker = create_health_checker(service.service_type)
        health_result = await health_checker.check_health(service)
        
        if not health_result.is_healthy:
            logger.warning(f"Service {service.name} is unhealthy: {health_result.error_message}")
            await registry.mark_service_unhealthy(service.id)
```

## 🔍 **Monitoring and Debugging**

### Logging
```python
import logging

# Service discovery logging
logger = logging.getLogger("kickai.service_discovery")

# Log service registration
logger.info(f"Registered service: {service.name} at {service.url}")

# Log health check results
logger.debug(f"Health check for {service.name}: {health_result.status}")

# Log circuit breaker state changes
logger.warning(f"Circuit breaker OPEN for service: {service.name}")
```

### Health Check Endpoints
```python
# Health check endpoint for monitoring
@app.get("/health/services")
async def get_service_health():
    registry = ServiceRegistry()
    health_status = {}
    
    for service in registry.get_all_services():
        health_result = await registry.check_service_health(service.id)
        health_status[service.name] = {
            "healthy": health_result.is_healthy,
            "last_check": health_result.timestamp,
            "error": health_result.error_message
        }
    
    return health_status
```

## 🛠️ **Maintenance and Operations**

### Service Discovery Maintenance
1. **Regular Health Checks**: Monitor service health continuously
2. **Configuration Updates**: Update service configurations as needed
3. **Performance Monitoring**: Monitor service discovery performance
4. **Error Analysis**: Analyze service discovery errors and failures

### Troubleshooting Common Issues
1. **Service Not Found**: Check service registration and naming
2. **Health Check Failures**: Verify health check URLs and service status
3. **Circuit Breaker Issues**: Check failure thresholds and recovery settings
4. **Configuration Errors**: Validate configuration file syntax and values

### Performance Optimization
1. **Health Check Frequency**: Optimize health check intervals
2. **Caching**: Implement service discovery result caching
3. **Connection Pooling**: Use connection pooling for health checks
4. **Batch Operations**: Batch service discovery operations when possible

## 📊 **Metrics and Monitoring**

### Key Metrics
- **Service Discovery Latency**: Time to discover services
- **Health Check Success Rate**: Percentage of successful health checks
- **Circuit Breaker State**: Current state of circuit breakers
- **Service Availability**: Percentage of services available

### Alerting
- **Service Down**: Alert when services become unavailable
- **Circuit Breaker Open**: Alert when circuit breakers open
- **Health Check Failures**: Alert on repeated health check failures
- **Configuration Errors**: Alert on service configuration issues

This service discovery system provides a robust foundation for managing services in the KICKAI architecture, ensuring high availability and resilient service interactions.