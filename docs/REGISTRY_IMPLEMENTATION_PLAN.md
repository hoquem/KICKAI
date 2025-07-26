# Registry Implementation Plan

## Immediate Action Items

### 1. **Fix Current Startup Issues** (Priority: Critical)

**Problem**: Bot startup failures due to registry initialization issues.

**Solution**: Implement fail-fast validation and proper error handling.

```python
# kickai/core/startup_validation/registry_validator.py
from typing import List, Dict, Any
from dataclasses import dataclass
from loguru import logger

@dataclass
class RegistryValidationResult:
    success: bool
    errors: List[str]
    warnings: List[str]
    registry_name: str

class RegistryStartupValidator:
    """Validates all registries during startup."""
    
    def __init__(self):
        self.validation_results: List[RegistryValidationResult] = []
    
    def validate_all_registries(self) -> bool:
        """Validate all registries and return success status."""
        logger.info("🔍 Validating all registries...")
        
        # Validate tool registry
        tool_result = self._validate_tool_registry()
        self.validation_results.append(tool_result)
        
        # Validate command registry
        command_result = self._validate_command_registry()
        self.validation_results.append(command_result)
        
        # Validate service registry
        service_result = self._validate_service_registry()
        self.validation_results.append(service_result)
        
        # Check overall success
        all_success = all(result.success for result in self.validation_results)
        
        if all_success:
            logger.info("✅ All registries validated successfully")
        else:
            logger.error("❌ Registry validation failed")
            for result in self.validation_results:
                if not result.success:
                    logger.error(f"❌ {result.registry_name}: {result.errors}")
        
        return all_success
    
    def _validate_tool_registry(self) -> RegistryValidationResult:
        """Validate tool registry."""
        errors = []
        warnings = []
        
        try:
            from kickai.agents.tool_registry import get_tool_registry
            registry = get_tool_registry()
            
            # Check if tools are discovered
            if not registry._discovered:
                errors.append("Tool registry not discovered")
            
            # Check if any tools are registered
            if not registry._tools:
                warnings.append("No tools registered")
            
            # Check for duplicate tool names
            tool_names = list(registry._tools.keys())
            if len(tool_names) != len(set(tool_names)):
                errors.append("Duplicate tool names found")
            
            return RegistryValidationResult(
                success=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                registry_name="Tool Registry"
            )
            
        except Exception as e:
            return RegistryValidationResult(
                success=False,
                errors=[f"Tool registry validation failed: {e}"],
                warnings=[],
                registry_name="Tool Registry"
            )
    
    def _validate_command_registry(self) -> RegistryValidationResult:
        """Validate command registry."""
        errors = []
        warnings = []
        
        try:
            from kickai.core.command_registry_initializer import get_initialized_command_registry
            registry = get_initialized_command_registry()
            
            # Check if commands are registered
            if not registry._commands:
                warnings.append("No commands registered")
            
            # Check for duplicate command names
            command_names = list(registry._commands.keys())
            if len(command_names) != len(set(command_names)):
                errors.append("Duplicate command names found")
            
            return RegistryValidationResult(
                success=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                registry_name="Command Registry"
            )
            
        except Exception as e:
            return RegistryValidationResult(
                success=False,
                errors=[f"Command registry validation failed: {e}"],
                warnings=[],
                registry_name="Command Registry"
            )
    
    def _validate_service_registry(self) -> RegistryValidationResult:
        """Validate service registry."""
        errors = []
        warnings = []
        
        try:
            from kickai.core.dependency_container import get_container
            container = get_container()
            
            # Check if container is initialized
            if not container._initialized:
                errors.append("Service container not initialized")
            
            # Check if required services are available
            required_services = [
                'PlayerService',
                'TeamService', 
                'DataStoreInterface'
            ]
            
            for service_name in required_services:
                try:
                    # This is a simplified check - in practice you'd check actual interfaces
                    pass
                except Exception:
                    errors.append(f"Required service {service_name} not available")
            
            return RegistryValidationResult(
                success=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                registry_name="Service Registry"
            )
            
        except Exception as e:
            return RegistryValidationResult(
                success=False,
                errors=[f"Service registry validation failed: {e}"],
                warnings=[],
                registry_name="Service Registry"
            )
```

### 2. **Implement Setuptools Entry Points** (Priority: High)

**Problem**: Manual discovery is error-prone and not standard Python.

**Solution**: Use setuptools entry points for automatic discovery.

```python
# setup.py (add to existing setup.py)
setup(
    name="kickai",
    version="1.0.0",
    # ... other setup parameters ...
    entry_points={
        'console_scripts': [
            'kickai-bot=kickai.cli:main',
        ],
        'kickai.tools': [
            'register_player=kickai.features.player_registration.domain.tools.registration_tools:register_player',
            'add_team_member=kickai.features.team_administration.domain.tools.team_tools:add_team_member',
            'send_message=kickai.features.communication.domain.tools.communication_tools:send_message',
        ],
        'kickai.commands': [
            'add=kickai.features.player_registration.application.commands.player_commands:handle_add',
            'status=kickai.features.player_registration.application.commands.player_commands:handle_status',
            'list=kickai.features.player_registration.application.commands.player_commands:handle_list',
        ],
        'kickai.services': [
            'player_service=kickai.features.player_registration.domain.services.player_service:PlayerService',
            'team_service=kickai.features.team_administration.domain.services.team_service:TeamService',
        ],
    },
)
```

**Updated Registry Discovery**:
```python
# kickai/core/registry_discovery.py
import pkg_resources
from typing import Dict, Any, List
from loguru import logger

class EntryPointDiscovery:
    """Discovers items from setuptools entry points."""
    
    @staticmethod
    def discover_tools() -> Dict[str, Any]:
        """Discover tools from entry points."""
        tools = {}
        
        for entry_point in pkg_resources.iter_entry_points('kickai.tools'):
            try:
                tool = entry_point.load()
                tools[entry_point.name] = tool
                logger.info(f"✅ Discovered tool: {entry_point.name}")
            except Exception as e:
                logger.error(f"❌ Failed to load tool {entry_point.name}: {e}")
        
        return tools
    
    @staticmethod
    def discover_commands() -> Dict[str, Any]:
        """Discover commands from entry points."""
        commands = {}
        
        for entry_point in pkg_resources.iter_entry_points('kickai.commands'):
            try:
                command = entry_point.load()
                commands[entry_point.name] = command
                logger.info(f"✅ Discovered command: {entry_point.name}")
            except Exception as e:
                logger.error(f"❌ Failed to load command {entry_point.name}: {e}")
        
        return commands
    
    @staticmethod
    def discover_services() -> Dict[str, Any]:
        """Discover services from entry points."""
        services = {}
        
        for entry_point in pkg_resources.iter_entry_points('kickai.services'):
            try:
                service_class = entry_point.load()
                services[entry_point.name] = service_class
                logger.info(f"✅ Discovered service: {entry_point.name}")
            except Exception as e:
                logger.error(f"❌ Failed to load service {entry_point.name}: {e}")
        
        return services
```

### 3. **Create Base Registry Classes** (Priority: High)

**Problem**: Inconsistent registry implementations.

**Solution**: Create unified base classes for all registries.

```python
# kickai/core/registry/base.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger

T = TypeVar('T')

class RegistryType(Enum):
    TOOL = "tool"
    COMMAND = "command"
    SERVICE = "service"

@dataclass
class RegistryItem(Generic[T]):
    name: str
    item: T
    metadata: Dict[str, Any] = field(default_factory=dict)
    registry_type: RegistryType = RegistryType.TOOL
    version: str = "1.0.0"
    enabled: bool = True
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

class BaseRegistry(ABC, Generic[T]):
    """Base registry class with common functionality."""
    
    def __init__(self, registry_type: RegistryType, name: str):
        self._items: Dict[str, RegistryItem[T]] = {}
        self._aliases: Dict[str, str] = {}
        self._registry_type = registry_type
        self._name = name
        self._initialized = False
        self._discovery_hooks: List[callable] = []
        
        logger.info(f"🔧 Initialized {name} ({registry_type.value})")
    
    @abstractmethod
    def register(self, name: str, item: T, **metadata) -> None:
        """Register an item with metadata."""
        pass
    
    @abstractmethod
    def get(self, name: str) -> Optional[T]:
        """Get an item by name."""
        pass
    
    def add_discovery_hook(self, hook: callable) -> None:
        """Add a discovery hook."""
        self._discovery_hooks.append(hook)
    
    def discover_from_entry_points(self, entry_point_group: str) -> None:
        """Discover items from setuptools entry points."""
        import pkg_resources
        
        for entry_point in pkg_resources.iter_entry_points(entry_point_group):
            try:
                item = entry_point.load()
                self.register(entry_point.name, item)
                logger.info(f"✅ Discovered {entry_point.name} from entry points")
            except Exception as e:
                logger.error(f"❌ Failed to load {entry_point.name}: {e}")
    
    def run_discovery_hooks(self) -> None:
        """Run all discovery hooks."""
        for hook in self._discovery_hooks:
            try:
                hook(self)
            except Exception as e:
                logger.error(f"❌ Discovery hook failed: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "name": self._name,
            "type": self._registry_type.value,
            "total_items": len(self._items),
            "total_aliases": len(self._aliases),
            "initialized": self._initialized,
            "enabled_items": len([item for item in self._items.values() if item.enabled])
        }
    
    def validate(self) -> List[str]:
        """Validate registry state."""
        errors = []
        
        # Check for duplicate names
        names = list(self._items.keys())
        if len(names) != len(set(names)):
            errors.append("Duplicate item names found")
        
        # Check for circular aliases
        for alias, target in self._aliases.items():
            if target in self._aliases and self._aliases[target] == alias:
                errors.append(f"Circular alias detected: {alias} <-> {target}")
        
        return errors
    
    def cleanup(self) -> None:
        """Clean up registry resources."""
        self._items.clear()
        self._aliases.clear()
        self._initialized = False
        logger.info(f"🧹 Cleaned up {self._name}")
```

### 4. **Implement Modern DI Container** (Priority: Medium)

**Problem**: Current DI container lacks scoping and lifecycle management.

**Solution**: Implement a modern DI container with proper scoping.

```python
# kickai/core/di/modern_container.py
from typing import Type, TypeVar, Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum
from loguru import logger

T = TypeVar('T')

class ServiceScope(Enum):
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    REQUEST = "request"

@dataclass
class ServiceRegistration:
    interface: Type
    implementation: Optional[Type] = None
    scope: ServiceScope = ServiceScope.SINGLETON
    factory: Optional[Callable] = None
    dependencies: Optional[list[Type]] = None

class ModernDIContainer:
    """Modern dependency injection container with scoping and lifecycle management."""
    
    def __init__(self):
        self._registrations: Dict[Type, ServiceRegistration] = {}
        self._singletons: Dict[Type, Any] = {}
        self._request_scope: Dict[Type, Any] = {}
        self._initialized = False
        
        logger.info("🔧 Modern DI Container initialized")
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a singleton service."""
        self._registrations[interface] = ServiceRegistration(
            interface=interface,
            implementation=implementation,
            scope=ServiceScope.SINGLETON
        )
        logger.debug(f"📝 Registered singleton: {interface.__name__}")
    
    def register_transient(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a transient service."""
        self._registrations[interface] = ServiceRegistration(
            interface=interface,
            implementation=implementation,
            scope=ServiceScope.TRANSIENT
        )
        logger.debug(f"📝 Registered transient: {interface.__name__}")
    
    def register_factory(self, interface: Type[T], factory: Callable) -> None:
        """Register a factory-based service."""
        self._registrations[interface] = ServiceRegistration(
            interface=interface,
            scope=ServiceScope.TRANSIENT,
            factory=factory
        )
        logger.debug(f"📝 Registered factory: {interface.__name__}")
    
    def resolve(self, interface: Type[T]) -> T:
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
        if hasattr(registration.implementation, '__init__'):
            import inspect
            sig = inspect.signature(registration.implementation.__init__)
            dependencies = {}
            
            for param_name, param in sig.parameters.items():
                if param_name != 'self' and param.annotation != inspect.Parameter.empty:
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
    
    def validate(self) -> List[str]:
        """Validate container configuration."""
        errors = []
        
        for interface, registration in self._registrations.items():
            if not registration.implementation and not registration.factory:
                errors.append(f"No implementation or factory for {interface.__name__}")
        
        return errors
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get container statistics."""
        return {
            "total_registrations": len(self._registrations),
            "singleton_instances": len(self._singletons),
            "request_scope_instances": len(self._request_scope),
            "initialized": self._initialized
        }
```

### 5. **Add Registry Monitoring and Metrics** (Priority: Medium)

**Problem**: No visibility into registry performance and usage.

**Solution**: Implement comprehensive monitoring.

```python
# kickai/core/monitoring/registry_monitor.py
import time
from typing import Dict, Any, List
from dataclasses import dataclass, field
from collections import defaultdict
from loguru import logger

@dataclass
class RegistryMetrics:
    name: str
    total_items: int = 0
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    average_response_time: float = 0.0
    errors: int = 0
    last_updated: float = field(default_factory=time.time)

class RegistryMonitor:
    """Monitors registry performance and usage."""
    
    def __init__(self):
        self._metrics: Dict[str, RegistryMetrics] = defaultdict(lambda: RegistryMetrics(""))
        self._request_times: Dict[str, List[float]] = defaultdict(list)
        self._enabled = True
        
        logger.info("📊 Registry Monitor initialized")
    
    def record_request(self, registry_name: str, item_name: str, success: bool, response_time: float) -> None:
        """Record a registry request."""
        if not self._enabled:
            return
        
        metrics = self._metrics[registry_name]
        metrics.name = registry_name
        metrics.total_requests += 1
        metrics.last_updated = time.time()
        
        if success:
            metrics.cache_hits += 1
        else:
            metrics.cache_misses += 1
            metrics.errors += 1
        
        # Update average response time
        self._request_times[registry_name].append(response_time)
        if len(self._request_times[registry_name]) > 100:  # Keep last 100 requests
            self._request_times[registry_name] = self._request_times[registry_name][-100:]
        
        metrics.average_response_time = sum(self._request_times[registry_name]) / len(self._request_times[registry_name])
    
    def record_item_count(self, registry_name: str, count: int) -> None:
        """Record the number of items in a registry."""
        if not self._enabled:
            return
        
        metrics = self._metrics[registry_name]
        metrics.name = registry_name
        metrics.total_items = count
        metrics.last_updated = time.time()
    
    def get_metrics(self, registry_name: str = None) -> Dict[str, Any]:
        """Get metrics for a specific registry or all registries."""
        if registry_name:
            return self._metrics[registry_name].__dict__
        
        return {
            name: metrics.__dict__ 
            for name, metrics in self._metrics.items()
        }
    
    def get_performance_report(self) -> str:
        """Generate a performance report."""
        if not self._metrics:
            return "No registry metrics available"
        
        report = ["📊 Registry Performance Report", ""]
        
        for name, metrics in self._metrics.items():
            report.append(f"**{name}**")
            report.append(f"  Total Items: {metrics.total_items}")
            report.append(f"  Total Requests: {metrics.total_requests}")
            report.append(f"  Cache Hit Rate: {metrics.cache_hits / max(metrics.total_requests, 1) * 100:.1f}%")
            report.append(f"  Average Response Time: {metrics.average_response_time * 1000:.2f}ms")
            report.append(f"  Errors: {metrics.errors}")
            report.append("")
        
        return "\n".join(report)
    
    def reset_metrics(self, registry_name: str = None) -> None:
        """Reset metrics for a specific registry or all registries."""
        if registry_name:
            self._metrics[registry_name] = RegistryMetrics(registry_name)
            self._request_times[registry_name].clear()
        else:
            self._metrics.clear()
            self._request_times.clear()
        
        logger.info(f"🔄 Reset metrics for {registry_name or 'all registries'}")
```

## Implementation Timeline

### Week 1: Foundation
- [ ] Create base registry classes
- [ ] Implement registry validation
- [ ] Add setuptools entry points
- [ ] Fix current startup issues

### Week 2: Modern DI
- [ ] Implement modern DI container
- [ ] Add service scoping
- [ ] Migrate existing services
- [ ] Add dependency validation

### Week 3: Monitoring
- [ ] Implement registry monitoring
- [ ] Add performance metrics
- [ ] Create health checks
- [ ] Add audit logging

### Week 4: Testing & Documentation
- [ ] Comprehensive testing
- [ ] Performance benchmarking
- [ ] Documentation updates
- [ ] Migration guide

## Success Metrics

### Performance
- **Startup time**: < 5 seconds
- **Registry lookup**: < 1ms average
- **Memory usage**: < 50MB for registries
- **Error rate**: < 0.1%

### Reliability
- **Uptime**: 99.9%
- **Recovery time**: < 30 seconds
- **Data consistency**: 100%
- **Backward compatibility**: 100%

### Maintainability
- **Code coverage**: > 90%
- **Documentation coverage**: 100%
- **Test automation**: 100%
- **Deployment automation**: 100%

## Risk Mitigation

### High Risk
- **Breaking changes**: Implement feature flags and gradual migration
- **Performance regression**: Comprehensive benchmarking
- **Data loss**: Backup and rollback procedures

### Medium Risk
- **Complexity increase**: Clear documentation and training
- **Integration issues**: Extensive testing
- **Learning curve**: Workshops and examples

### Low Risk
- **Minor bugs**: Automated testing and monitoring
- **Documentation gaps**: Regular reviews
- **Performance optimization**: Continuous monitoring

## Conclusion

This implementation plan provides a clear path to modernize the registry implementations while maintaining backward compatibility and improving reliability. The phased approach ensures minimal disruption while delivering significant improvements in performance, maintainability, and observability. 