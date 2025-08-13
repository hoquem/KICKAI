"""
Configuration Validator

This module provides comprehensive validation for KICKAI configuration files,
ensuring consistency between agent configurations, tool assignments, and command routing.
"""

import re
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import yaml

from kickai.core.enums import AgentRole, ChatType, CommandType, PermissionLevel

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Represents a configuration validation error."""
    file_path: str
    error_type: str
    message: str
    severity: str  # 'error', 'warning', 'info'
    location: Optional[str] = None


@dataclass
class ValidationResult:
    """Results of configuration validation."""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    info: List[ValidationError]
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
    
    def get_all_issues(self) -> List[ValidationError]:
        """Get all validation issues (errors, warnings, info)."""
        return self.errors + self.warnings + self.info


class ConfigValidator:
    """
    Comprehensive configuration validator for KICKAI.
    
    Validates:
    - Agent configuration (agents.yaml)
    - Command routing configuration (command_routing.yaml)  
    - Task configuration (tasks.yaml)
    - Cross-file consistency
    - Tool assignment consistency
    - Agent role validation
    """

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the configuration validator.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent
        self.agents_config: Dict[str, Any] = {}
        self.routing_config: Dict[str, Any] = {}
        self.tasks_config: Dict[str, Any] = {}
        self.validation_errors: List[ValidationError] = []
        self.validation_warnings: List[ValidationError] = []
        self.validation_info: List[ValidationError] = []

    def validate_all_configurations(self) -> ValidationResult:
        """
        Validate all configuration files and check cross-file consistency.
        
        Returns:
            ValidationResult with all validation issues
        """
        logger.info("🔍 Starting comprehensive configuration validation...")
        
        # Reset validation results
        self._reset_validation_results()
        
        # Load all configuration files
        self._load_configurations()
        
        # Validate individual files - STRICT MODE
        self._validate_agents_config()
        self._validate_routing_config()
        self._validate_tasks_config()
        
        # Cross-validation - STRICT MODE
        self._validate_cross_file_consistency()
        
        # Additional strict validation
        self._strict_validation_checks()
        
        # Create result
        result = ValidationResult(
            is_valid=len(self.validation_errors) == 0,
            errors=self.validation_errors.copy(),
            warnings=self.validation_warnings.copy(),
            info=self.validation_info.copy()
        )
        
        # Log results
        self._log_validation_results(result)
        
        return result

    def _reset_validation_results(self) -> None:
        """Reset validation results."""
        self.validation_errors.clear()
        self.validation_warnings.clear()
        self.validation_info.clear()

    def _load_configurations(self) -> None:
        """Load all configuration files."""
        # Load agents.yaml
        agents_path = self.config_dir / "agents.yaml"
        if agents_path.exists():
            try:
                with open(agents_path, 'r', encoding='utf-8') as f:
                    self.agents_config = yaml.safe_load(f)
                logger.debug(f"Loaded agents configuration: {agents_path}")
            except Exception as e:
                self._add_error("agents.yaml", "loading", f"Failed to load agents.yaml: {e}")

        # Load command_routing.yaml
        routing_path = self.config_dir / "command_routing.yaml"
        if routing_path.exists():
            try:
                with open(routing_path, 'r', encoding='utf-8') as f:
                    self.routing_config = yaml.safe_load(f)
                logger.debug(f"Loaded routing configuration: {routing_path}")
            except Exception as e:
                self._add_error("command_routing.yaml", "loading", f"Failed to load command_routing.yaml: {e}")

        # Load tasks.yaml
        tasks_path = self.config_dir / "tasks.yaml"
        if tasks_path.exists():
            try:
                with open(tasks_path, 'r', encoding='utf-8') as f:
                    self.tasks_config = yaml.safe_load(f)
                logger.debug(f"Loaded tasks configuration: {tasks_path}")
            except Exception as e:
                self._add_error("tasks.yaml", "loading", f"Failed to load tasks.yaml: {e}")

    def _validate_agents_config(self) -> None:
        """Validate agents.yaml configuration."""
        if not self.agents_config:
            self._add_error("agents.yaml", "missing", "agents.yaml configuration not found or empty")
            return

        # Validate agent definitions
        agents = self.agents_config.get('agents', [])
        if not agents:
            self._add_error("agents.yaml", "structure", "No agents defined in configuration")
            return

        # Check for required agent roles - use lowercase for comparison
        required_roles = {role.value.lower() for role in AgentRole}
        configured_agents = set()
        
        for agent in agents:
            if not isinstance(agent, dict):
                self._add_error("agents.yaml", "structure", "Agent definition must be a dictionary")
                continue
                
            agent_name = agent.get('name', '')
            if not agent_name:
                self._add_error("agents.yaml", "structure", "Agent must have a name")
                continue
                
            configured_agents.add(agent_name.lower())
            
            # Validate agent structure
            self._validate_single_agent(agent, agent_name)

        # Check if all required agents are configured
        missing_agents = required_roles - configured_agents
        if missing_agents:
            self._add_warning("agents.yaml", "completeness", 
                f"Missing agent configurations: {', '.join(missing_agents)}")

        # Check for unknown agents
        unknown_agents = configured_agents - required_roles
        if unknown_agents:
            self._add_warning("agents.yaml", "unknown", 
                f"Unknown agent configurations: {', '.join(unknown_agents)}")

    def _validate_single_agent(self, agent_config: Dict[str, Any], agent_name: str) -> None:
        """Validate a single agent configuration."""
        required_fields = ['role', 'goal', 'backstory', 'tools']
        
        for field in required_fields:
            if field not in agent_config:
                self._add_error("agents.yaml", "structure", 
                    f"Agent '{agent_name}' missing required field: {field}")
            elif not agent_config[field]:
                self._add_warning("agents.yaml", "content", 
                    f"Agent '{agent_name}' has empty {field}")

        # Validate tools list
        tools = agent_config.get('tools', [])
        if not isinstance(tools, list):
            self._add_error("agents.yaml", "structure", 
                f"Agent '{agent_name}' tools must be a list")
        elif len(tools) == 0:
            self._add_warning("agents.yaml", "content", 
                f"Agent '{agent_name}' has no tools assigned")

        # Validate entity types
        entity_types = agent_config.get('entity_types', [])
        if entity_types and not isinstance(entity_types, list):
            self._add_error("agents.yaml", "structure", 
                f"Agent '{agent_name}' entity_types must be a list")

    def _validate_routing_config(self) -> None:
        """Validate command_routing.yaml configuration."""
        if not self.routing_config:
            self._add_error("command_routing.yaml", "missing", 
                "command_routing.yaml configuration not found or empty")
            return

        # Validate structure - STRICT MODE
        required_sections = ['command_routing', 'default_routing']
        for section in required_sections:
            if section not in self.routing_config:
                self._add_error("command_routing.yaml", "structure", 
                    f"REQUIRED section missing: {section}")

        # Validate command routing rules - STRICT MODE
        self._validate_command_routing_rules()
        
        # Pattern routing removed - validate it's not present
        if 'pattern_routing' in self.routing_config and self.routing_config['pattern_routing'].get('patterns'):
            self._add_error("command_routing.yaml", "deprecated",
                "Pattern routing is no longer supported - use exact command matching only")
        
        # Validate agent constraints
        self._validate_agent_constraints()

    def _validate_command_routing_rules(self) -> None:
        """Validate command routing rules."""
        command_routing = self.routing_config.get('command_routing', {})
        
        all_commands = set()
        valid_agents = {role.value.lower() for role in AgentRole}
        
        for rule_name, rule_config in command_routing.items():
            if not isinstance(rule_config, dict):
                self._add_error("command_routing.yaml", "structure", 
                    f"Routing rule '{rule_name}' must be a dictionary")
                continue
                
            # Check required fields
            if 'agent' not in rule_config:
                self._add_error("command_routing.yaml", "structure", 
                    f"Routing rule '{rule_name}' missing 'agent' field")
                continue
                
            agent = rule_config['agent']
            if agent not in valid_agents:
                self._add_error("command_routing.yaml", "reference", 
                    f"Invalid agent '{agent}' in rule '{rule_name}'. Valid agents: {valid_agents}")
                    
            # Check commands
            commands = rule_config.get('commands', [])
            if not isinstance(commands, list):
                self._add_error("command_routing.yaml", "structure", 
                    f"Commands in rule '{rule_name}' must be a list")
                continue
                
            # Check for duplicate commands
            for command in commands:
                if command in all_commands:
                    self._add_warning("command_routing.yaml", "duplicate", 
                        f"Command '{command}' defined in multiple rules")
                all_commands.add(command)

    def _strict_validation_checks(self) -> None:
        """Additional strict validation to ensure no silent failures."""
        # Validate that all commands have explicit routing (no defaults)
        self._validate_complete_command_coverage()
        
        # Validate that configuration doesn't contain deprecated features
        self._validate_no_deprecated_features()
        
        # Validate that error handling is explicit, not silent
        self._validate_explicit_error_handling()

    def _validate_complete_command_coverage(self) -> None:
        """Ensure all expected commands have explicit routing (with flexible slash matching)."""
        expected_commands = {
            '/help', '/info', '/myinfo', '/status', '/addplayer', '/addmember',
            '/attendance', '/list', '/ping', '/version', '/announce'
        }
        
        configured_commands = set()
        command_routing = self.routing_config.get('command_routing', {})
        
        for rule_config in command_routing.values():
            if isinstance(rule_config, dict):
                commands = rule_config.get('commands', [])
                configured_commands.update(commands)
        
        # With flexible matching, check if expected commands are covered
        # by configured commands (considering both slash and non-slash variants)
        missing_commands = set()
        for expected_cmd in expected_commands:
            is_covered = False
            for configured_cmd in configured_commands:
                # Check if they match with flexible slash handling
                expected_without_slash = expected_cmd.lower().lstrip('/')
                configured_without_slash = configured_cmd.lower().lstrip('/')
                
                if expected_without_slash == configured_without_slash:
                    is_covered = True
                    break
            
            if not is_covered:
                missing_commands.add(expected_cmd)
        
        if missing_commands:
            self._add_error("command_routing.yaml", "completeness",
                f"Missing explicit routing for commands: {sorted(missing_commands)}")

    def _validate_no_deprecated_features(self) -> None:
        """Ensure configuration doesn't use deprecated features."""
        # Check for caching configuration
        optimization = self.routing_config.get('optimization', {})
        if 'caching' in optimization:
            self._add_error("command_routing.yaml", "deprecated",
                "Caching configuration is deprecated - removed for simplicity")

    def _validate_explicit_error_handling(self) -> None:
        """Ensure error handling is explicit and not silent."""
        error_handling = self.routing_config.get('error_handling', {})
        
        # Require explicit error handling
        required_error_types = ['unknown_command', 'agent_unavailable', 'permission_denied']
        for error_type in required_error_types:
            if error_type not in error_handling:
                self._add_error("command_routing.yaml", "error_handling",
                    f"Missing explicit error handling for: {error_type}")
            else:
                action = error_handling[error_type].get('action')
                if not action:
                    self._add_error("command_routing.yaml", "error_handling",
                        f"Missing action for error type: {error_type}")

    def _validate_agent_constraints(self) -> None:
        """Validate agent constraints configuration."""
        agent_constraints = self.routing_config.get('agent_constraints', {})
        valid_agents = {role.value.lower() for role in AgentRole}
        
        for agent, constraints in agent_constraints.items():
            if agent not in valid_agents:
                self._add_error("command_routing.yaml", "reference", 
                    f"Invalid agent '{agent}' in agent_constraints")
                continue
                
            # Validate constraint structure
            if not isinstance(constraints, dict):
                self._add_error("command_routing.yaml", "structure", 
                    f"Constraints for agent '{agent}' must be a dictionary")
                continue
                
            # Validate specific constraints
            max_requests = constraints.get('max_concurrent_requests')
            if max_requests is not None and (not isinstance(max_requests, int) or max_requests < 1):
                self._add_error("command_routing.yaml", "value", 
                    f"max_concurrent_requests for agent '{agent}' must be a positive integer")

    def _validate_tasks_config(self) -> None:
        """Validate tasks.yaml configuration."""
        if not self.tasks_config:
            self._add_info("tasks.yaml", "optional", "tasks.yaml not found (optional)")
            return

        # Validate task templates if they exist
        tasks = self.tasks_config.get('tasks', [])
        for i, task in enumerate(tasks):
            if not isinstance(task, dict):
                self._add_error("tasks.yaml", "structure", 
                    f"Task {i} must be a dictionary")
                continue
                
            # Check required fields
            if 'name' not in task:
                self._add_error("tasks.yaml", "structure", 
                    f"Task {i} missing 'name' field")
                    
            if 'agent' in task:
                agent = task['agent']
                valid_agents = {role.value.lower() for role in AgentRole}
                if agent.lower() not in valid_agents:
                    self._add_error("tasks.yaml", "reference", 
                        f"Invalid agent '{agent}' in task {i}")

    def _validate_cross_file_consistency(self) -> None:
        """Validate consistency between configuration files."""
        # Check agent-command routing consistency
        self._validate_agent_command_consistency()
        
        # Check tool assignments vs routing
        self._validate_tool_routing_consistency()

    def _validate_agent_command_consistency(self) -> None:
        """Validate that agents referenced in routing exist in agents config."""
        if not self.agents_config or not self.routing_config:
            return
            
        # Get configured agents
        configured_agents = set()
        agents = self.agents_config.get('agents', [])
        for agent in agents:
            if isinstance(agent, dict) and 'name' in agent:
                configured_agents.add(agent['name'].lower())
        
        # Check routing references
        command_routing = self.routing_config.get('command_routing', {})
        for rule_name, rule_config in command_routing.items():
            if isinstance(rule_config, dict):
                agent = rule_config.get('agent')
                if agent and agent.lower() not in configured_agents:
                    self._add_error("cross-file", "consistency", 
                        f"Routing rule '{rule_name}' references undefined agent '{agent}'")

    def _validate_tool_routing_consistency(self) -> None:
        """Validate that tool assignments match routing expectations."""
        if not self.agents_config or not self.routing_config:
            return
            
        # This is a complex validation that would require tool registry
        # For now, add as informational
        self._add_info("cross-file", "analysis", 
            "Tool-routing consistency validation requires runtime tool registry")

    def _add_error(self, file_path: str, error_type: str, message: str, location: str = None) -> None:
        """Add a validation error."""
        self.validation_errors.append(ValidationError(
            file_path=file_path,
            error_type=error_type,
            message=message,
            severity='error',
            location=location
        ))

    def _add_warning(self, file_path: str, error_type: str, message: str, location: str = None) -> None:
        """Add a validation warning."""
        self.validation_warnings.append(ValidationError(
            file_path=file_path,
            error_type=error_type,
            message=message,
            severity='warning',
            location=location
        ))

    def _add_info(self, file_path: str, error_type: str, message: str, location: str = None) -> None:
        """Add validation info."""
        self.validation_info.append(ValidationError(
            file_path=file_path,
            error_type=error_type,
            message=message,
            severity='info',
            location=location
        ))

    def _log_validation_results(self, result: ValidationResult) -> None:
        """Log validation results."""
        if result.is_valid:
            logger.info(f"✅ Configuration validation passed")
        else:
            logger.error(f"❌ Configuration validation failed with {len(result.errors)} errors")
            
        if result.warnings:
            logger.warning(f"⚠️ {len(result.warnings)} validation warnings")
            
        if result.info:
            logger.info(f"ℹ️ {len(result.info)} informational messages")

    def validate_specific_file(self, file_type: str) -> ValidationResult:
        """
        Validate a specific configuration file.
        
        Args:
            file_type: Type of file to validate ('agents', 'routing', 'tasks')
            
        Returns:
            ValidationResult for the specific file
        """
        self._reset_validation_results()
        self._load_configurations()
        
        if file_type == 'agents':
            self._validate_agents_config()
        elif file_type == 'routing':
            self._validate_routing_config()
        elif file_type == 'tasks':
            self._validate_tasks_config()
        else:
            self._add_error("validator", "parameter", f"Unknown file type: {file_type}")
            
        return ValidationResult(
            is_valid=len(self.validation_errors) == 0,
            errors=self.validation_errors.copy(),
            warnings=self.validation_warnings.copy(),
            info=self.validation_info.copy()
        )


def validate_configuration(config_dir: Optional[str] = None) -> ValidationResult:
    """
    Convenience function to validate all configurations.
    
    Args:
        config_dir: Directory containing configuration files
        
    Returns:
        ValidationResult with all validation issues
    """
    validator = ConfigValidator(config_dir)
    return validator.validate_all_configurations()


def print_validation_results(result: ValidationResult) -> None:
    """
    Print validation results in a human-readable format.
    
    Args:
        result: ValidationResult to print
    """
    print("\n" + "="*60)
    print("KICKAI CONFIGURATION VALIDATION RESULTS")
    print("="*60)
    
    if result.is_valid:
        print("✅ VALIDATION PASSED")
    else:
        print("❌ VALIDATION FAILED")
    
    print(f"\nSummary:")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Warnings: {len(result.warnings)}")  
    print(f"  Info: {len(result.info)}")
    
    # Print errors
    if result.errors:
        print(f"\n❌ ERRORS ({len(result.errors)}):")
        for error in result.errors:
            location = f" at {error.location}" if error.location else ""
            print(f"  [{error.file_path}] {error.error_type}: {error.message}{location}")
    
    # Print warnings
    if result.warnings:
        print(f"\n⚠️ WARNINGS ({len(result.warnings)}):")
        for warning in result.warnings:
            location = f" at {warning.location}" if warning.location else ""
            print(f"  [{warning.file_path}] {warning.error_type}: {warning.message}{location}")
    
    # Print info (only if no errors/warnings)
    if result.info and not result.errors and not result.warnings:
        print(f"\nℹ️ INFORMATION ({len(result.info)}):")
        for info in result.info:
            location = f" at {info.location}" if info.location else ""
            print(f"  [{info.file_path}] {info.error_type}: {info.message}{location}")
    
    print("\n" + "="*60)