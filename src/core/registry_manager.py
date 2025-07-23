#!/usr/bin/env python3
"""
Registry Manager for KICKAI System

This module provides a centralized manager for all system registries.
It follows the single source of truth principle and ensures clean, loosely coupled architecture.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from loguru import logger

from core.command_registry_initializer import get_initialized_command_registry
from core.command_registry import CommandRegistry
from core.agent_registry import get_agent_registry, AgentRegistry
from agents.tool_registry import get_tool_registry, ToolRegistry


class RegistryType(Enum):
    """Types of registries in the system."""
    COMMAND = "command"
    AGENT = "agent"
    TOOL = "tool"
    TASK = "task"


@dataclass
class RegistryInfo:
    """Information about a registry."""
    registry_type: RegistryType
    name: str
    description: str
    total_items: int
    enabled_items: int
    features: List[str]
    last_updated: str


class RegistryManager:
    """
    Centralized registry manager for the KICKAI system.
    
    This manager provides:
    - Single source of truth for all registries
    - Coordinated discovery and registration
    - System-wide statistics and health checks
    - Dependency management between registries
    - Clean, loosely coupled architecture
    """
    
    def __init__(self):
        """Initialize the registry manager."""
        self._registries: Dict[RegistryType, Any] = {}
        self._initialized = False
        
        logger.info("🔧 RegistryManager initialized")
    
    def initialize_registries(self, src_path: str = "src") -> None:
        """
        Initialize all registries with auto-discovery.
        
        Args:
            src_path: Path to source directory for discovery
        """
        if self._initialized:
            logger.info("Registries already initialized, skipping")
            return
        
        try:
            # Initialize command registry
            command_registry = get_initialized_command_registry()
            self._registries[RegistryType.COMMAND] = command_registry
            
            # Initialize tool registry
            tool_registry = get_tool_registry()
            tool_registry.auto_discover_tools(src_path)
            self._registries[RegistryType.TOOL] = tool_registry
            
            # Initialize agent registry
            agent_registry = get_agent_registry()
            agent_registry.auto_discover_agents(src_path)
            self._registries[RegistryType.AGENT] = agent_registry
            
            self._initialized = True
            logger.info("✅ All registries initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing registries: {e}")
            raise
    
    def get_registry(self, registry_type: RegistryType) -> Any:
        """Get a specific registry by type."""
        if not self._initialized:
            self.initialize_registries()
        
        return self._registries.get(registry_type)
    
    def get_command_registry(self) -> CommandRegistry:
        """Get the command registry."""
        return self.get_registry(RegistryType.COMMAND)
    
    def get_agent_registry(self) -> AgentRegistry:
        """Get the agent registry."""
        return self.get_registry(RegistryType.AGENT)
    
    def get_tool_registry(self) -> ToolRegistry:
        """Get the tool registry."""
        return self.get_registry(RegistryType.TOOL)
    
    def get_registry_info(self, registry_type: RegistryType) -> Optional[RegistryInfo]:
        """Get information about a specific registry."""
        registry = self.get_registry(registry_type)
        if not registry:
            return None
        
        if registry_type == RegistryType.COMMAND:
            stats = registry.get_command_statistics()
            return RegistryInfo(
                registry_type=registry_type,
                name="Command Registry",
                description="Manages all system commands and their metadata",
                total_items=stats.get('total_commands', 0),
                enabled_items=stats.get('total_commands', 0),  # All commands are enabled by default
                features=list(stats.get('commands_by_feature', {}).keys()),
                last_updated="Now"
            )
        
        elif registry_type == RegistryType.AGENT:
            stats = registry.get_agent_statistics()
            return RegistryInfo(
                registry_type=registry_type,
                name="Agent Registry",
                description="Manages all system agents and their configurations",
                total_items=stats.get('total_agents', 0),
                enabled_items=stats.get('enabled_agents', 0),
                features=stats.get('features_with_agents', []),
                last_updated="Now"
            )
        
        elif registry_type == RegistryType.TOOL:
            stats = registry.get_tool_statistics()
            return RegistryInfo(
                registry_type=registry_type,
                name="Tool Registry",
                description="Manages all system tools and their metadata",
                total_items=stats.get('total_tools', 0),
                enabled_items=stats.get('enabled_tools', 0),
                features=stats.get('features_with_tools', []),
                last_updated="Now"
            )
        
        return None
    
    def get_all_registry_info(self) -> List[RegistryInfo]:
        """Get information about all registries."""
        info_list = []
        
        for registry_type in RegistryType:
            info = self.get_registry_info(registry_type)
            if info:
                info_list.append(info)
        
        return info_list
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        if not self._initialized:
            self.initialize_registries()
        
        stats = {
            'total_registries': len(self._registries),
            'registries': {}
        }
        
        for registry_type, registry in self._registries.items():
            if registry_type == RegistryType.COMMAND:
                stats['registries']['commands'] = registry.get_command_statistics()
            elif registry_type == RegistryType.AGENT:
                stats['registries']['agents'] = registry.get_agent_statistics()
            elif registry_type == RegistryType.TOOL:
                stats['registries']['tools'] = registry.get_tool_statistics()
        
        return stats
    
    def validate_registry_dependencies(self) -> Dict[str, List[str]]:
        """
        Validate dependencies between registries.
        
        Returns:
            Dictionary of validation results
        """
        validation_results = {
            'errors': [],
            'warnings': [],
            'success': []
        }
        
        try:
            # Validate agent-tool dependencies
            agent_registry = self.get_agent_registry()
            tool_registry = self.get_tool_registry()
            
            if agent_registry and tool_registry:
                for agent in agent_registry.list_all_agents():
                    for tool_name in agent.tools:
                        tool_metadata = tool_registry.get_tool(tool_name)
                        if not tool_metadata:
                            validation_results['errors'].append(
                                f"Agent '{agent.agent_id}' references missing tool '{tool_name}'"
                            )
                        elif not tool_metadata.enabled:
                            validation_results['warnings'].append(
                                f"Agent '{agent.agent_id}' references disabled tool '{tool_name}'"
                            )
                        else:
                            validation_results['success'].append(
                                f"Agent '{agent.agent_id}' tool dependency '{tool_name}' validated"
                            )
            
            # Validate command-agent dependencies
            command_registry = self.get_command_registry()
            if command_registry and agent_registry:
                for command in command_registry.list_all_commands():
                    # Check if command has associated agent handlers
                    # This would depend on your command implementation
                    pass
            
        except Exception as e:
            validation_results['errors'].append(f"Validation error: {str(e)}")
        
        return validation_results
    
    def search_across_registries(self, query: str) -> Dict[str, List[Any]]:
        """
        Search across all registries for a query.
        
        Args:
            query: Search query string
            
        Returns:
            Dictionary of search results by registry type
        """
        results = {
            'commands': [],
            'agents': [],
            'tools': []
        }
        
        # Search commands
        command_registry = self.get_command_registry()
        if command_registry:
            # Note: Command registry doesn't have search yet, but we can implement it
            pass
        
        # Search agents
        agent_registry = self.get_agent_registry()
        if agent_registry:
            results['agents'] = agent_registry.search_agents(query)
        
        # Search tools
        tool_registry = self.get_tool_registry()
        if tool_registry:
            results['tools'] = tool_registry.search_tools(query)
        
        return results
    
    def get_feature_overview(self, feature_name: str) -> Dict[str, Any]:
        """
        Get comprehensive overview of a specific feature.
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            Dictionary with feature overview
        """
        overview = {
            'feature_name': feature_name,
            'commands': [],
            'agents': [],
            'tools': [],
            'total_items': 0
        }
        
        # Get commands for feature
        command_registry = self.get_command_registry()
        if command_registry:
            commands = command_registry.get_commands_by_feature(feature_name)
            overview['commands'] = [cmd.name for cmd in commands]
        
        # Get agents for feature
        agent_registry = self.get_agent_registry()
        if agent_registry:
            agents = agent_registry.get_agents_by_feature(feature_name)
            overview['agents'] = [agent.agent_id for agent in agents]
        
        # Get tools for feature
        tool_registry = self.get_tool_registry()
        if tool_registry:
            tools = tool_registry.get_tools_by_feature(feature_name)
            overview['tools'] = [tool.tool_id for tool in tools]
        
        # Calculate total
        overview['total_items'] = (
            len(overview['commands']) + 
            len(overview['agents']) + 
            len(overview['tools'])
        )
        
        return overview
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on all registries.
        
        Returns:
            Health check results
        """
        health_results = {
            'status': 'healthy',
            'registries': {},
            'issues': [],
            'recommendations': []
        }
        
        try:
            # Check each registry
            for registry_type in RegistryType:
                registry = self.get_registry(registry_type)
                if registry:
                    registry_info = self.get_registry_info(registry_type)
                    health_results['registries'][registry_type.value] = {
                        'status': 'healthy',
                        'total_items': registry_info.total_items if registry_info else 0,
                        'enabled_items': registry_info.enabled_items if registry_info else 0
                    }
                else:
                    health_results['registries'][registry_type.value] = {
                        'status': 'missing',
                        'total_items': 0,
                        'enabled_items': 0
                    }
                    health_results['issues'].append(f"Registry {registry_type.value} not found")
            
            # Validate dependencies
            validation_results = self.validate_registry_dependencies()
            if validation_results['errors']:
                health_results['status'] = 'unhealthy'
                health_results['issues'].extend(validation_results['errors'])
            
            if validation_results['warnings']:
                health_results['recommendations'].extend(validation_results['warnings'])
            
            # Check for empty registries
            for registry_type, info in health_results['registries'].items():
                if info['total_items'] == 0:
                    health_results['recommendations'].append(
                        f"Registry {registry_type} is empty - consider adding items"
                    )
            
        except Exception as e:
            health_results['status'] = 'error'
            health_results['issues'].append(f"Health check error: {str(e)}")
        
        return health_results
    
    def export_registry_data(self, registry_type: Optional[RegistryType] = None) -> Dict[str, Any]:
        """
        Export registry data for backup or analysis.
        
        Args:
            registry_type: Specific registry to export, or None for all
            
        Returns:
            Dictionary with exported data
        """
        export_data = {
            'timestamp': 'Now',
            'version': '1.0.0',
            'data': {}
        }
        
        if registry_type:
            registry = self.get_registry(registry_type)
            if registry:
                if registry_type == RegistryType.COMMAND:
                    export_data['data']['commands'] = [
                        {
                            'name': cmd.name,
                            'description': cmd.description,
                            'feature': cmd.feature,
                            'permission_level': cmd.permission_level.value
                        }
                        for cmd in registry.list_all_commands()
                    ]
                elif registry_type == RegistryType.AGENT:
                    export_data['data']['agents'] = [
                        {
                            'agent_id': agent.agent_id,
                            'name': agent.name,
                            'description': agent.description,
                            'feature_module': agent.feature_module,
                            'enabled': agent.enabled
                        }
                        for agent in registry.list_all_agents()
                    ]
                elif registry_type == RegistryType.TOOL:
                    export_data['data']['tools'] = [
                        {
                            'tool_id': tool.tool_id,
                            'name': tool.name,
                            'description': tool.description,
                            'feature_module': tool.feature_module,
                            'enabled': tool.enabled
                        }
                        for tool in registry.list_all_tools()
                    ]
        else:
            # Export all registries
            for reg_type in RegistryType:
                export_data['data'][reg_type.value] = self.export_registry_data(reg_type)['data']
        
        return export_data


# Global registry manager instance
_registry_manager: Optional[RegistryManager] = None


def get_registry_manager() -> RegistryManager:
    """Get the global registry manager instance."""
    global _registry_manager
    if _registry_manager is None:
        _registry_manager = RegistryManager()
    return _registry_manager


def initialize_system_registries(src_path: str = "src") -> None:
    """Initialize all system registries."""
    manager = get_registry_manager()
    manager.initialize_registries(src_path)


def get_system_statistics() -> Dict[str, Any]:
    """Get comprehensive system statistics."""
    manager = get_registry_manager()
    return manager.get_system_statistics()


def health_check_registries() -> Dict[str, Any]:
    """Perform health check on all registries."""
    manager = get_registry_manager()
    return manager.health_check() 