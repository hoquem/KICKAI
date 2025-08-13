"""
Command Routing Manager

This module provides dynamic command-to-agent routing based on YAML configuration,
replacing hardcoded routing logic with a flexible, maintainable configuration system.
"""

import re
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Union
# Removed: caching system imports for simplicity

import yaml

from kickai.core.enums import AgentRole, ChatType

logger = logging.getLogger(__name__)


@dataclass
class RoutingDecision:
    """Represents a routing decision for a command."""
    agent_role: AgentRole
    command: str
    match_type: str  # 'exact', 'pattern', 'default', 'fallback'
    confidence: float  # 0.0 to 1.0
    context_valid: bool
    error_message: Optional[str] = None


@dataclass
class RoutingRule:
    """Represents a command routing rule."""
    agent: str
    commands: List[str]
    description: str
    priority: int
    patterns: Optional[List[Pattern]] = None


class CommandRoutingManager:
    """
    Manages dynamic command routing based on YAML configuration.
    
    This class replaces hardcoded routing logic in crew_agents.py with a 
    flexible, configuration-driven approach that supports:
    - Exact command matching
    - Pattern-based routing  
    - Context-aware routing (chat type, permissions)
    - Caching for performance
    - Comprehensive validation
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the command routing manager.
        
        Args:
            config_path: Path to command_routing.yaml file
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config: Dict[str, Any] = {}
        self.routing_rules: Dict[str, RoutingRule] = {}
        self.pattern_rules: List[tuple] = []
        self.chat_type_rules: Dict[str, Dict[str, Any]] = {}
        self.agent_constraints: Dict[str, Dict[str, Any]] = {}
        self._last_loaded = None  # Simplified: just track if loaded
        
        # Load configuration
        self.reload_configuration()

    def _get_default_config_path(self) -> str:
        """Get the default path to command_routing.yaml."""
        return str(Path(__file__).parent / "command_routing.yaml")

    def reload_configuration(self) -> None:
        """Reload configuration from YAML file."""
        try:
            logger.info(f"Loading command routing configuration from: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            self._process_configuration()
            self._validate_configuration()
            
            self._last_loaded = True  # Simplified: just mark as loaded
            logger.info("✅ Command routing configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load command routing configuration: {e}")
            raise RuntimeError(f"Failed to load command routing configuration: {e}")

    def _process_configuration(self) -> None:
        """Process loaded configuration into internal data structures."""
        # Process command routing rules
        command_routing = self.config.get('command_routing', {})
        self.routing_rules = {}
        
        for rule_name, rule_config in command_routing.items():
            if not isinstance(rule_config, dict):
                continue
                
            self.routing_rules[rule_name] = RoutingRule(
                agent=rule_config.get('agent', ''),
                commands=rule_config.get('commands', []),
                description=rule_config.get('description', ''),
                priority=rule_config.get('priority', 999)
            )

        # Pattern routing removed for simplicity
        self.pattern_rules = []  # Keep empty list for compatibility

        # Process context routing
        context_routing = self.config.get('context_routing', {})
        self.chat_type_rules = context_routing.get('chat_type_rules', {})
        
        # Process agent constraints
        self.agent_constraints = self.config.get('agent_constraints', {})
        
        # Caching removed for simplicity
        
        logger.debug(f"Processed {len(self.routing_rules)} routing rules")
        logger.debug(f"Processed {len(self.pattern_rules)} pattern rules")

    def _validate_configuration(self) -> None:
        """Validate the loaded configuration."""
        # Validate agent references - convert to lowercase for comparison
        valid_agents = set(role.value.lower() for role in AgentRole)
        
        for rule_name, rule in self.routing_rules.items():
            if rule.agent not in valid_agents:
                raise ValueError(f"Invalid agent '{rule.agent}' in rule '{rule_name}'. Valid agents: {valid_agents}")
        
        for pattern, agent, _ in self.pattern_rules:
            if agent not in valid_agents:
                raise ValueError(f"Invalid agent '{agent}' in pattern rule. Valid agents: {valid_agents}")
        
        # Validate default routing
        default_routing = self.config.get('default_routing', {})
        default_agent = default_routing.get('default_agent', '')
        fallback_agent = default_routing.get('fallback_agent', '')
        
        if default_agent and default_agent not in valid_agents:
            raise ValueError(f"Invalid default agent '{default_agent}'. Valid agents: {valid_agents}")
        
        if fallback_agent and fallback_agent not in valid_agents:
            raise ValueError(f"Invalid fallback agent '{fallback_agent}'. Valid agents: {valid_agents}")
        
        logger.debug("✅ Configuration validation passed")

    def route_command(
        self, 
        command: str, 
        chat_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> RoutingDecision:
        """
        Route a command to the appropriate agent.
        
        Args:
            command: The command to route (e.g., "/help", "/info")
            chat_type: The chat context ("main", "leadership", "private")
            context: Additional context for routing decisions
            
        Returns:
            RoutingDecision with agent assignment and metadata
        """
        # Normalize command (caching removed for simplicity)
        normalized_command = self._normalize_command(command)
        
        # Check context-based restrictions first
        if chat_type:
            restriction_result = self._check_context_restrictions(normalized_command, chat_type)
            if restriction_result:
                return restriction_result

        # Try exact command matching
        exact_match = self._find_exact_match(normalized_command)
        if exact_match:
            return RoutingDecision(
                agent_role=self._convert_agent_name_to_role(exact_match.agent),
                command=normalized_command,
                match_type='exact',
                confidence=1.0,
                context_valid=self._validate_context(exact_match.agent, context or {})
            )

        # Pattern matching removed for simplicity

        # Default routing
        default_agent = self.config.get('default_routing', {}).get('default_agent', 'message_processor')
        return RoutingDecision(
            agent_role=self._convert_agent_name_to_role(default_agent),
            command=normalized_command,
            match_type='default',
            confidence=0.5,
            context_valid=self._validate_context(default_agent, context or {})
        )

    def _normalize_command(self, command: str) -> str:
        """Normalize command for consistent matching."""
        command = command.strip().lower()
        
        # Strip prefix if configured
        default_routing = self.config.get('default_routing', {})
        if default_routing.get('strip_prefix', True):
            if command.startswith('/'):
                # Keep the '/' for internal processing but normalize
                pass
        
        return command

    def _convert_agent_name_to_role(self, agent_name: str) -> AgentRole:
        """Convert agent name from config to AgentRole enum."""
        # Map lowercase names to proper enum values
        name_mapping = {
            "message_processor": AgentRole.MESSAGE_PROCESSOR,
            "help_assistant": AgentRole.HELP_ASSISTANT,
            "player_coordinator": AgentRole.PLAYER_COORDINATOR,
            "team_administrator": AgentRole.TEAM_ADMINISTRATOR,
            "squad_selector": AgentRole.SQUAD_SELECTOR
        }
        
        if agent_name in name_mapping:
            return name_mapping[agent_name]
        
        # Try to find by enum value (case-insensitive)
        for role in AgentRole:
            if role.value.lower() == agent_name.lower():
                return role
        
        # Default fallback
        return AgentRole.MESSAGE_PROCESSOR

    def _check_context_restrictions(self, command: str, chat_type: str) -> Optional[RoutingDecision]:
        """Check if command is restricted with flexible slash matching."""
        chat_rules = self.chat_type_rules.get(chat_type, {})
        blocked_commands = chat_rules.get('blocked_commands', [])
        
        # Normalize input command
        normalized_cmd = command.lower().strip()
        
        # Check if command is blocked using flexible matching
        is_blocked = False
        for blocked_cmd in blocked_commands:
            # Try exact match first
            if normalized_cmd == blocked_cmd.lower():
                is_blocked = True
                break
            
            # Try flexible slash matching
            blocked_without_slash = blocked_cmd.lower().lstrip('/')
            input_without_slash = normalized_cmd.lstrip('/')
            
            if blocked_without_slash == input_without_slash:
                is_blocked = True
                break
        
        if is_blocked:
            redirect_agent = chat_rules.get('redirect_agent', 'message_processor')
            return RoutingDecision(
                agent_role=self._convert_agent_name_to_role(redirect_agent),
                command=command,
                match_type='context_restricted',
                confidence=1.0,
                context_valid=True,
                error_message=self.config.get('error_handling', {}).get('permission_denied', {}).get('response_template', 
                    "❌ You don't have permission to use this command in this chat.")
            )
        
        return None

    def _find_exact_match(self, command: str) -> Optional[RoutingRule]:
        """Find exact command match with flexible slash handling."""
        # Sort rules by priority (lower number = higher priority)
        sorted_rules = sorted(self.routing_rules.items(), key=lambda x: x[1].priority)
        
        # Normalize input command
        normalized_cmd = command.lower().strip()
        
        for rule_name, rule in sorted_rules:
            for config_command in rule.commands:
                # Try exact match first (case insensitive)
                if normalized_cmd == config_command.lower():
                    logger.debug(f"Exact match found: {command} → {rule.agent} (rule: {rule_name})")
                    return rule
                
                # Try flexible slash matching
                # If config has "/info", also match "info"
                # If config has "help", also match "/help"
                config_without_slash = config_command.lower().lstrip('/')
                input_without_slash = normalized_cmd.lstrip('/')
                
                if config_without_slash == input_without_slash:
                    logger.debug(f"Flexible match found: {command} → {rule.agent} (rule: {rule_name}) [slash-flexible]")
                    return rule
        
        return None

    # Pattern matching removed for simplicity

    def _validate_context(self, agent: str, context: Dict[str, Any]) -> bool:
        """Validate that required context is available for the agent."""
        agent_constraints = self.agent_constraints.get(agent, {})
        required_context = agent_constraints.get('requires_context', [])
        
        for required_key in required_context:
            if required_key not in context or context[required_key] is None:
                logger.debug(f"Missing required context '{required_key}' for agent {agent}")
                return False
        
        return True

    # Caching methods removed for simplicity

    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing statistics and metrics (simplified)."""
        return {
            'configuration_loaded': bool(self._last_loaded),
            'routing_rules_count': len(self.routing_rules),
            'agents_configured': list(self.agent_constraints.keys()),
            'chat_type_rules': list(self.chat_type_rules.keys())
        }

    def get_commands_for_agent(self, agent: str) -> List[str]:
        """Get all commands routed to a specific agent."""
        commands = []
        
        for rule in self.routing_rules.values():
            if rule.agent == agent:
                commands.extend(rule.commands)
        
        return sorted(list(set(commands)))

    def validate_agent_assignment(self, agent: str, command: str) -> bool:
        """Validate that a command should be assigned to the given agent."""
        decision = self.route_command(command)
        return decision.agent_role.value == agent

    def get_fallback_agent(self) -> str:
        """Get the configured fallback agent."""
        return self.config.get('default_routing', {}).get('fallback_agent', 'message_processor')

    def is_configuration_valid(self) -> tuple[bool, List[str]]:
        """Check if current configuration is valid."""
        errors = []
        
        try:
            self._validate_configuration()
            return True, []
        except Exception as e:
            errors.append(str(e))
            return False, errors


# Global instance (lazily initialized)
_routing_manager: Optional[CommandRoutingManager] = None


def get_command_routing_manager() -> CommandRoutingManager:
    """Get the global command routing manager instance."""
    global _routing_manager
    if _routing_manager is None:
        _routing_manager = CommandRoutingManager()
    return _routing_manager


def route_command_to_agent(
    command: str, 
    chat_type: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> RoutingDecision:
    """
    Convenience function to route a command to an agent.
    
    Args:
        command: The command to route
        chat_type: Chat context
        context: Additional context
        
    Returns:
        RoutingDecision with agent assignment
    """
    manager = get_command_routing_manager()
    return manager.route_command(command, chat_type, context)