"""
Configuration-Driven Service Definitions

Allows services to be defined and configured through configuration files,
further reducing tight coupling and enabling environment-specific service definitions.
"""

import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

from .interfaces import ServiceDefinition, ServiceType, ServiceConfiguration

logger = logging.getLogger(__name__)


class ServiceConfigurationLoader:
    """Loads service definitions from configuration files."""
    
    def __init__(self, config_paths: List[str] = None):
        """Initialize with default or custom config paths."""
        self.config_paths = config_paths or [
            "config/services.json",
            "config/services.yaml",
            "config/services.yml",
            "kickai/config/services.json",
            "kickai/config/services.yaml",
        ]
    
    def load_service_definitions(self) -> List[ServiceDefinition]:
        """Load service definitions from configuration files."""
        all_definitions = []
        
        for config_path in self.config_paths:
            path = Path(config_path)
            if path.exists():
                try:
                    definitions = self._load_from_file(path)
                    all_definitions.extend(definitions)
                    logger.info(f"✅ Loaded {len(definitions)} service definitions from {config_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load service definitions from {config_path}: {e}")
        
        if not all_definitions:
            logger.info("📝 No service configuration files found, using default definitions")
            all_definitions = self._get_default_service_definitions()
        
        return all_definitions
    
    def _load_from_file(self, path: Path) -> List[ServiceDefinition]:
        """Load service definitions from a single file."""
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix.lower() in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        return self._parse_service_definitions(data)
    
    def _parse_service_definitions(self, data: Dict[str, Any]) -> List[ServiceDefinition]:
        """Parse service definitions from loaded data."""
        definitions = []
        
        services_config = data.get('services', [])
        if isinstance(services_config, dict):
            # Convert dict format to list format
            services_config = [
                {'name': name, **config} 
                for name, config in services_config.items()
            ]
        
        for service_config in services_config:
            try:
                definition = self._create_service_definition(service_config)
                definitions.append(definition)
            except Exception as e:
                logger.error(f"❌ Failed to parse service definition {service_config.get('name', 'unknown')}: {e}")
        
        return definitions
    
    def _create_service_definition(self, config: Dict[str, Any]) -> ServiceDefinition:
        """Create a ServiceDefinition from configuration data."""
        # Required fields
        name = config['name']
        service_type_str = config.get('type', 'utility')
        
        # Convert string to ServiceType enum
        try:
            service_type = ServiceType(service_type_str.lower())
        except ValueError:
            logger.warning(f"⚠️ Unknown service type '{service_type_str}' for service '{name}', defaulting to UTILITY")
            service_type = ServiceType.UTILITY
        
        # Optional fields
        interface_name = config.get('interface')
        implementation_class = config.get('implementation')
        dependencies = config.get('dependencies', [])
        health_check_enabled = config.get('health_check_enabled', True)
        health_check_interval = config.get('health_check_interval', 60)
        timeout = config.get('timeout', 30.0)
        retry_count = config.get('retry_count', 3)
        metadata = config.get('metadata', {})
        
        # Add configuration source to metadata
        metadata['configuration_source'] = 'config_file'
        
        return ServiceDefinition(
            name=name,
            service_type=service_type,
            interface_name=interface_name,
            implementation_class=implementation_class,
            dependencies=dependencies,
            health_check_enabled=health_check_enabled,
            health_check_interval=health_check_interval,
            timeout=timeout,
            retry_count=retry_count,
            metadata=metadata
        )
    
    def _get_default_service_definitions(self) -> List[ServiceDefinition]:
        """Get default service definitions when no config files are found."""
        return [
            # Core Services
            ServiceDefinition(
                name="DataStoreInterface",
                service_type=ServiceType.CORE,
                interface_name="kickai.database.interfaces.DataStoreInterface",
                dependencies=[],
                timeout=10.0,
                metadata={"priority": "critical", "startup_required": True}
            ),
            ServiceDefinition(
                name="DependencyContainer", 
                service_type=ServiceType.CORE,
                implementation_class="kickai.core.dependency_container.DependencyContainer",
                dependencies=[],
                timeout=5.0,
                metadata={"priority": "critical", "startup_required": True}
            ),
            
            # Feature Services
            ServiceDefinition(
                name="PlayerService",
                service_type=ServiceType.FEATURE,
                interface_name="kickai.features.player_registration.domain.interfaces.player_service_interface.IPlayerService",
                implementation_class="kickai.features.player_registration.domain.services.player_service.PlayerService",
                dependencies=["DataStoreInterface"],
                timeout=15.0,
                metadata={"feature": "player_registration"}
            ),
            ServiceDefinition(
                name="TeamService",
                service_type=ServiceType.FEATURE,
                interface_name="kickai.features.team_administration.domain.interfaces.team_service_interface.ITeamService",
                implementation_class="kickai.features.team_administration.domain.services.team_service.TeamService",
                dependencies=["DataStoreInterface"],
                timeout=15.0,
                metadata={"feature": "team_administration"}
            ),
            ServiceDefinition(
                name="MatchService",
                service_type=ServiceType.FEATURE,
                interface_name="kickai.features.match_management.domain.interfaces.match_service_interface.IMatchService",
                implementation_class="kickai.features.match_management.domain.services.match_service.MatchService",
                dependencies=["DataStoreInterface", "PlayerService", "TeamService"],
                timeout=20.0,
                metadata={"feature": "match_management"}
            ),
            
            # External Services
            ServiceDefinition(
                name="FirebaseClient",
                service_type=ServiceType.EXTERNAL,
                implementation_class="kickai.database.firebase_client.FirebaseClient",
                dependencies=[],
                timeout=30.0,
                retry_count=5,
                metadata={"external_provider": "firebase", "connection_required": True}
            ),
            ServiceDefinition(
                name="TelegramBot",
                service_type=ServiceType.EXTERNAL,
                dependencies=["TeamService", "PlayerService"],
                timeout=25.0,
                retry_count=3,
                metadata={"external_provider": "telegram", "connection_required": True}
            ),
            
            # Agent Services
            ServiceDefinition(
                name="AgentFactory",
                service_type=ServiceType.CORE,
                implementation_class="kickai.agents.simplified_agent_factory.SimplifiedAgentFactory",
                dependencies=["DependencyContainer"],
                timeout=20.0,
                metadata={"agent_system": True, "startup_required": True}
            ),
            ServiceDefinition(
                name="CrewAISystem",
                service_type=ServiceType.CORE,
                dependencies=["AgentFactory", "PlayerService", "TeamService"],
                timeout=30.0,
                metadata={"agent_system": True, "orchestration": True}
            ),
        ]


def load_service_configuration() -> ServiceConfiguration:
    """Load service discovery system configuration."""
    config_paths = [
        "config/service_discovery.json",
        "config/service_discovery.yaml",
        "kickai/config/service_discovery.json",
    ]
    
    for config_path in config_paths:
        path = Path(config_path)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    if path.suffix.lower() in ['.yaml', '.yml']:
                        data = yaml.safe_load(f)
                    else:
                        data = json.load(f)
                
                return _parse_service_configuration(data)
            except Exception as e:
                logger.warning(f"⚠️ Failed to load service discovery configuration from {config_path}: {e}")
    
    logger.info("📝 No service discovery configuration found, using defaults")
    return ServiceConfiguration()


def _parse_service_configuration(data: Dict[str, Any]) -> ServiceConfiguration:
    """Parse service configuration from loaded data."""
    config_data = data.get('service_discovery', {})
    
    return ServiceConfiguration(
        auto_discovery_enabled=config_data.get('auto_discovery_enabled', True),
        health_check_enabled=config_data.get('health_check_enabled', True),
        health_check_interval=config_data.get('health_check_interval', 60),
        service_timeout=config_data.get('service_timeout', 30.0),
        retry_attempts=config_data.get('retry_attempts', 3),
        circuit_breaker_enabled=config_data.get('circuit_breaker_enabled', True),
        circuit_breaker_threshold=config_data.get('circuit_breaker_threshold', 5),
        circuit_breaker_timeout=config_data.get('circuit_breaker_timeout', 60),
        startup_service_types=[
            ServiceType(t.lower()) for t in config_data.get('startup_service_types', 
                ['core', 'feature', 'external', 'utility'])
        ]
    )


def create_example_service_config() -> Dict[str, Any]:
    """Create an example service configuration file."""
    return {
        "service_discovery": {
            "auto_discovery_enabled": True,
            "health_check_enabled": True,
            "health_check_interval": 60,
            "service_timeout": 30.0,
            "retry_attempts": 3,
            "circuit_breaker_enabled": True,
            "circuit_breaker_threshold": 5,
            "circuit_breaker_timeout": 60,
            "startup_service_types": ["core", "feature", "external", "utility"]
        },
        "services": [
            {
                "name": "DataStoreInterface",
                "type": "core",
                "interface": "kickai.database.interfaces.DataStoreInterface",
                "dependencies": [],
                "timeout": 10.0,
                "health_check_enabled": True,
                "metadata": {
                    "priority": "critical",
                    "startup_required": True
                }
            },
            {
                "name": "PlayerService", 
                "type": "feature",
                "interface": "kickai.features.player_registration.domain.interfaces.player_service_interface.IPlayerService",
                "implementation": "kickai.features.player_registration.domain.services.player_service.PlayerService",
                "dependencies": ["DataStoreInterface"],
                "timeout": 15.0,
                "health_check_enabled": True,
                "metadata": {
                    "feature": "player_registration"
                }
            }
        ]
    }


def write_example_config_file(path: str = "config/services.json") -> None:
    """Write an example configuration file."""
    config = create_example_service_config()
    
    config_path = Path(path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        if config_path.suffix.lower() in ['.yaml', '.yml']:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        else:
            json.dump(config, f, indent=2)
    
    logger.info(f"✅ Example service configuration written to {path}")


# Convenience functions
def get_service_definitions() -> List[ServiceDefinition]:
    """Get all service definitions from configuration."""
    loader = ServiceConfigurationLoader()
    return loader.load_service_definitions()


def get_service_discovery_config() -> ServiceConfiguration:
    """Get service discovery configuration."""
    return load_service_configuration()