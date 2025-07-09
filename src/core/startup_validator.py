"""
Pre-flight Checks / Health Checks Module

A dedicated StartupValidator module performs a series of configurable
checks, organized by category (LLM, agent, tool, task, external
services). It uses Dependency Injection and can be configured via
config.yaml or environment variables.
"""

import asyncio
import logging
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Type
from pathlib import Path

from src.core.improved_config_system import ImprovedConfigurationManager
from src.core.enums import AIProvider
from src.database.firebase_client import FirebaseClient
from src.services.team_mapping_service import TeamMappingService

logger = logging.getLogger(__name__)


class CheckStatus(Enum):
    """Status of a health check."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"
    SKIPPED = "SKIPPED"


class CheckCategory(Enum):
    """Categories of health checks."""
    LLM = "LLM"
    AGENT = "AGENT"
    TOOL = "TOOL"
    TASK = "TASK"
    EXTERNAL_SERVICE = "EXTERNAL_SERVICE"
    CONFIGURATION = "CONFIGURATION"
    DATABASE = "DATABASE"
    TELEGRAM = "TELEGRAM"


@dataclass
class CheckResult:
    """Result of a health check."""
    name: str
    category: CheckCategory
    status: CheckStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    error: Optional[Exception] = None


@dataclass
class ValidationReport:
    """Complete validation report."""
    overall_status: CheckStatus
    checks: List[CheckResult] = field(default_factory=list)
    summary: Dict[CheckCategory, Dict[CheckStatus, int]] = field(default_factory=dict)
    critical_failures: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def add_check(self, check: CheckResult) -> None:
        """Add a check result to the report."""
        self.checks.append(check)
        
        # Update summary
        if check.category not in self.summary:
            self.summary[check.category] = {status: 0 for status in CheckStatus}
        self.summary[check.category][check.status] += 1
        
        # Track critical failures and warnings
        if check.status == CheckStatus.FAILED:
            self.critical_failures.append(f"{check.category.value}: {check.name} - {check.message}")
        elif check.status == CheckStatus.WARNING:
            self.warnings.append(f"{check.category.value}: {check.name} - {check.message}")

    def is_healthy(self) -> bool:
        """Check if the system is healthy (no critical failures)."""
        return len(self.critical_failures) == 0


class HealthCheck(ABC):
    """Abstract base class for health checks."""
    
    def __init__(self, name: str, category: CheckCategory, critical: bool = True):
        self.name = name
        self.category = category
        self.critical = critical
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        """Execute the health check."""
        pass
    
    def __str__(self) -> str:
        return f"{self.category.value}:{self.name}"


class ConfigurationCheck(HealthCheck):
    """Check configuration loading and validation."""
    
    def __init__(self):
        super().__init__("Configuration Loading", CheckCategory.CONFIGURATION, critical=True)
    
    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        start_time = asyncio.get_event_loop().time()
        
        try:
            config_manager = ImprovedConfigurationManager()
            config = config_manager.configuration
            
            # Validate essential configuration
            required_fields = [
                'provider', 'api_key', 'model_name', 'max_retries'
            ]
            ai_config = config.ai
            missing_fields = []
            for field in required_fields:
                if not hasattr(ai_config, field) or getattr(ai_config, field) is None:
                    missing_fields.append(field)
            
            if not config.teams or not config.teams.default_team_id:
                missing_fields.append('default_team_id')
            if not config.teams or not config.teams.teams:
                missing_fields.append('teams')
            if not config.telegram or not config.telegram.bot_token:
                missing_fields.append('bot_token')
            
            if missing_fields:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message=f"Missing required configuration fields: {missing_fields}",
                    details={'missing_fields': missing_fields},
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                )
            
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.PASSED,
                message="Configuration loaded successfully",
                details={'provider': str(ai_config.provider), 'team_id': config.teams.default_team_id},
                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
            )
        except Exception as e:
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.FAILED,
                message=f"Exception during configuration check: {e}",
                details={'exception': str(e)},
                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
            )


class LLMProviderCheck(HealthCheck):
    """Check LLM provider configuration and connectivity."""
    
    def __init__(self):
        super().__init__("LLM Provider", CheckCategory.LLM, critical=True)
    
    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        start_time = asyncio.get_event_loop().time()
        
        try:
            config_manager = ImprovedConfigurationManager()
            config = config_manager.configuration
            
            if config.ai.provider != AIProvider.GOOGLE_GEMINI:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message=f"Unsupported AI provider: {config.ai.provider}. Only GOOGLE_GEMINI is supported.",
                    details={'provider': str(config.ai.provider)},
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                )
            
            if not config.ai.api_key:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message="Google API key is not configured",
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                )
            
            # Test LLM connectivity (basic test)
            try:
                import google.generativeai as genai
                genai.configure(api_key=config.ai.api_key)
                model = genai.GenerativeModel(config.ai.model_name)
                response = model.generate_content("Hello")
                if response.text:
                    return CheckResult(
                        name=self.name,
                        category=self.category,
                        status=CheckStatus.PASSED,
                        message="LLM provider configured and responsive",
                        details={'provider': str(config.ai.provider), 'model': config.ai.model_name},
                        duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                    )
            except Exception as e:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message=f"LLM connectivity test failed: {str(e)}",
                    error=e,
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                )
                
        except Exception as e:
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.FAILED,
                message=f"LLM provider check failed: {str(e)}",
                error=e,
                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
            )


class AgentInitializationCheck(HealthCheck):
    """Check agent instantiation, configuration integrity, LLM assignment, and AgentRole mapping."""
    
    def __init__(self):
        super().__init__("Agent Validation", CheckCategory.AGENT, critical=True)
    
    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        start_time = asyncio.get_event_loop().time()
        errors = []
        warnings = []
        details = {}
        try:
            from src.agents.crew_agents import TeamManagementSystem, AgentFactory, AgentRole, BaseTeamAgent
            team_id = context.get('team_id', 'KAI')
            logger.info(f"[AGENT VALIDATION] Starting for team {team_id}")
            team_system = TeamManagementSystem(team_id)
            # 1. Agent instantiation and type check
            agent_details = {}
            for role, agent in team_system.agents.items():
                role_name = role.value if hasattr(role, 'value') else str(role)
                agent_type = type(agent).__name__
                # Check correct class
                expected_class = AgentFactory.AGENT_CLASSES.get(role)
                if expected_class is None:
                    errors.append(f"No agent class mapped for AgentRole {role_name}")
                elif not isinstance(agent, expected_class):
                    errors.append(f"Agent for {role_name} is {agent_type}, expected {expected_class.__name__}")
                # 2. Config integrity
                config = getattr(agent, 'agent_config', None)
                if not config:
                    errors.append(f"Agent {role_name} missing agent_config")
                else:
                    for field in ['max_iterations', 'enabled', 'allow_delegation', 'verbose']:
                        if not hasattr(config, field):
                            errors.append(f"Agent {role_name} config missing field: {field}")
                # 3. LLM assignment
                llm = getattr(agent, 'llm', None)
                if llm is None:
                    errors.append(f"Agent {role_name} has no LLM assigned")
                agent_details[role_name] = {
                    'type': agent_type,
                    'config': {f: getattr(config, f, None) for f in ['max_iterations', 'enabled', 'allow_delegation', 'verbose']} if config else None,
                    'llm_type': type(llm).__name__ if llm else None
                }
            # 4. AgentRole enum-to-class mapping
            missing_roles = []
            for role in AgentRole:
                if role not in AgentFactory.AGENT_CLASSES:
                    missing_roles.append(role.value)
            if missing_roles:
                errors.append(f"AgentRole(s) missing from AgentFactory.AGENT_CLASSES: {missing_roles}")
            # 5. Extra classes not mapped to AgentRole
            extra_classes = [r for r in AgentFactory.AGENT_CLASSES if r not in AgentRole]
            if extra_classes:
                warnings.append(f"Extra agent class mappings not in AgentRole: {extra_classes}")
            logger.info(f"[AGENT VALIDATION] Details: {agent_details}")
            details['agent_details'] = agent_details
            details['missing_roles'] = missing_roles
            details['extra_classes'] = extra_classes
            duration = (asyncio.get_event_loop().time() - start_time) * 1000
            if errors:
                logger.error(f"[AGENT VALIDATION] Errors: {errors}")
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message=f"Agent validation failed: {errors}",
                    details=details,
                    duration_ms=duration
                )
            if warnings:
                logger.warning(f"[AGENT VALIDATION] Warnings: {warnings}")
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.WARNING,
                    message=f"Agent validation warnings: {warnings}",
                    details=details,
                    duration_ms=duration
                )
            logger.info(f"[AGENT VALIDATION] All agent checks passed.")
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.PASSED,
                message=f"All agents validated successfully ({len(agent_details)} agents)",
                details=details,
                duration_ms=duration
            )
        except Exception as e:
            logger.error(f"[AGENT VALIDATION] Exception: {e}")
            logger.error(traceback.format_exc())
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.FAILED,
                message=f"Agent validation exception: {e}",
                details={'traceback': traceback.format_exc()},
                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
            )


class ToolConfigurationCheck(HealthCheck):
    """Check tool configuration and availability."""
    
    def __init__(self):
        super().__init__("Tool Configuration", CheckCategory.TOOL, critical=True)
    
    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        start_time = asyncio.get_event_loop().time()
        
        try:
            from src.domain.tools.communication_tools import SendMessageTool, SendAnnouncementTool
            from src.domain.tools.logging_tools import LogCommandTool
            from src.domain.tools.team_management_tools import GetAllPlayersTool, GetPlayerStatusTool
            
            # Test tool instantiation with required fields
            team_id = context.get('team_id', 'KAI')
            
            tools_to_test = [
                (SendMessageTool, {'team_id': team_id}),
                (SendAnnouncementTool, {'team_id': team_id}),
                (LogCommandTool, {'team_id': team_id}),
                (GetAllPlayersTool, {'team_id': team_id, 'command_operations': None}),
                (GetPlayerStatusTool, {'team_id': team_id, 'command_operations': None}),
            ]
            
            failed_tools = []
            successful_tools = []
            
            for tool_class, kwargs in tools_to_test:
                try:
                    tool = tool_class(**kwargs)
                    successful_tools.append(tool_class.__name__)
                except Exception as e:
                    failed_tools.append(f"{tool_class.__name__}: {str(e)}")
            
            if failed_tools:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message=f"Tool configuration failed for: {', '.join(failed_tools)}",
                    details={'failed_tools': failed_tools, 'successful_tools': successful_tools},
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                )
            
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.PASSED,
                message=f"All tools configured successfully ({len(successful_tools)} tools)",
                details={'successful_tools': successful_tools},
                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
            )
            
        except Exception as e:
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.FAILED,
                message=f"Tool configuration check failed: {str(e)}",
                error=e,
                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
            )


class DatabaseConnectivityCheck(HealthCheck):
    """Check database connectivity and configuration."""
    
    def __init__(self):
        super().__init__("Database Connectivity", CheckCategory.DATABASE, critical=True)
    
    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Test Firebase connectivity
            from src.database.firebase_client import FirebaseClient
            from src.core.improved_config_system import get_improved_config
            
            config = get_improved_config().configuration.database
            client = FirebaseClient(config)
            
            # Test basic connectivity
            collections = await client.list_collections()
            
            duration = (asyncio.get_event_loop().time() - start_time) * 1000
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.PASSED,
                message="Database connectivity successful",
                details={'database': 'Firebase Firestore', 'test_collection': 'health_check_test', 'collections_count': len(collections)},
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (asyncio.get_event_loop().time() - start_time) * 1000
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.FAILED,
                message=f"Database connectivity failed: {str(e)}",
                error=e,
                duration_ms=duration
            )


class TeamMappingCheck(HealthCheck):
    """Check team mapping service configuration."""
    
    def __init__(self):
        super().__init__("Team Mapping", CheckCategory.CONFIGURATION, critical=True)
    
    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        start_time = asyncio.get_event_loop().time()
        
        try:
            team_mapping_service = TeamMappingService()
            
            # Check if mappings exist
            mappings = team_mapping_service.get_all_mappings()
            
            if not mappings:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message="No team mappings configured",
                    details={'mappings_count': 0},
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                )
            
            # Validate mapping structure
            valid_mappings = []
            invalid_mappings = []
            
            for team_id, mapping in mappings.items():
                required_fields = ['team_id', 'bot_token', 'bot_username', 'chat_ids']
                missing_fields = [field for field in required_fields if not hasattr(mapping, field)]
                
                if missing_fields:
                    invalid_mappings.append(f"{team_id}: missing {missing_fields}")
                else:
                    valid_mappings.append(team_id)
            
            if invalid_mappings:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message=f"Invalid team mappings: {', '.join(invalid_mappings)}",
                    details={'valid_mappings': valid_mappings, 'invalid_mappings': invalid_mappings},
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                )
            
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.PASSED,
                message=f"Team mapping configuration valid ({len(valid_mappings)} mappings)",
                details={'valid_mappings': valid_mappings},
                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
            )
            
        except Exception as e:
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.FAILED,
                message=f"Team mapping check failed: {str(e)}",
                error=e,
                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
            )


class CrewValidationCheck(HealthCheck):
    """Verify Crew instantiation, agent assignment, and end-to-end task execution."""
    
    def __init__(self):
        super().__init__("Crew Validation", CheckCategory.AGENT, critical=True)
    
    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        start_time = asyncio.get_event_loop().time()
        errors = []
        warnings = []
        
        try:
            from src.agents.crew_agents import TeamManagementSystem
            from src.agents.intelligent_system import CapabilityBasedRouter
            
            team_id = context.get('team_id', 'KAI')
            logger.info(f"[CrewValidation] Starting crew validation for team {team_id}")
            
            # 1. Test TeamManagementSystem instantiation
            logger.info(f"[CrewValidation] Testing TeamManagementSystem instantiation...")
            try:
                team_system = TeamManagementSystem(team_id)
                logger.info(f"[CrewValidation] ✅ TeamManagementSystem instantiated successfully")
            except Exception as e:
                error_msg = f"Failed to instantiate TeamManagementSystem: {str(e)}"
                logger.error(f"[CrewValidation] ❌ {error_msg}")
                errors.append(error_msg)
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message="Crew instantiation failed",
                    details={'errors': errors},
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                )
            
            # 2. Check agent assignment and availability
            logger.info(f"[CrewValidation] Checking agent assignment and availability...")
            try:
                # Check if agents are available
                available_agents = getattr(team_system, 'agents', {})
                logger.info(f"[CrewValidation] Available agents: {list(available_agents.keys()) if available_agents else 'None'}")
                
                if not available_agents:
                    error_msg = "No agents available in TeamManagementSystem"
                    logger.error(f"[CrewValidation] ❌ {error_msg}")
                    errors.append(error_msg)
                else:
                    logger.info(f"[CrewValidation] ✅ {len(available_agents)} agents available")
                    
                    # Check each agent's configuration
                    for agent_name, agent in available_agents.items():
                        logger.info(f"[CrewValidation] Agent {agent_name}: {type(agent).__name__}")
                        if hasattr(agent, 'enabled'):
                            logger.info(f"[CrewValidation]   Enabled: {agent.enabled}")
                        if hasattr(agent, 'tools'):
                            logger.info(f"[CrewValidation]   Tools: {len(agent.tools) if agent.tools else 0}")
                
            except Exception as e:
                error_msg = f"Failed to check agent assignment: {str(e)}"
                logger.error(f"[CrewValidation] ❌ {error_msg}")
                errors.append(error_msg)
            
            # 3. Test agent routing capability
            logger.info(f"[CrewValidation] Testing agent routing capability...")
            try:
                # Test with a simple intent that should route to an agent
                test_intent = {
                    "primary_intent": "status_inquiry",
                    "confidence": 0.98,
                    "secondary_intents": [],
                    "entities": {},
                    "context": {"urgency": "low", "complexity": "simple"}
                }
                
                # Try to route the intent
                if hasattr(team_system, '_route_intent'):
                    routed_agents = team_system._route_intent(test_intent)
                    logger.info(f"[CrewValidation] Routed agents for status_inquiry: {routed_agents}")
                    
                    if not routed_agents:
                        error_msg = "No agents routed for status_inquiry intent"
                        logger.error(f"[CrewValidation] ❌ {error_msg}")
                        errors.append(error_msg)
                    else:
                        logger.info(f"[CrewValidation] ✅ Successfully routed to {len(routed_agents)} agents")
                else:
                    logger.warning(f"[CrewValidation] ⚠️ TeamManagementSystem has no _route_intent method")
                    
            except Exception as e:
                error_msg = f"Failed to test agent routing: {str(e)}"
                logger.error(f"[CrewValidation] ❌ {error_msg}")
                errors.append(error_msg)
            
            # 4. Test end-to-end task execution
            logger.info(f"[CrewValidation] Testing end-to-end task execution...")
            try:
                # Simple test task
                test_task = "What is 1+1?"
                test_context = {
                    'user_id': 'test_user',
                    'chat_id': 'test_chat',
                    'team_id': team_id,
                    'user_role': 'player'
                }
                
                result = team_system.execute_task(test_task, test_context)
                logger.info(f"[CrewValidation] ✅ End-to-end task execution successful")
                logger.info(f"[CrewValidation] Result length: {len(str(result))}")
                
            except Exception as e:
                error_msg = f"Failed to execute end-to-end task: {str(e)}"
                logger.error(f"[CrewValidation] ❌ {error_msg}")
                errors.append(error_msg)
            
            # 5. Check crew-level settings
            logger.info(f"[CrewValidation] Checking crew-level settings...")
            try:
                # Check if the system has required attributes
                required_attrs = ['llm', 'capability_matrix', 'task_decomposer']
                for attr in required_attrs:
                    if hasattr(team_system, attr):
                        logger.info(f"[CrewValidation] ✅ {attr} available")
                    else:
                        warning_msg = f"Missing {attr} attribute"
                        logger.warning(f"[CrewValidation] ⚠️ {warning_msg}")
                        warnings.append(warning_msg)
                        
            except Exception as e:
                error_msg = f"Failed to check crew-level settings: {str(e)}"
                logger.error(f"[CrewValidation] ❌ {error_msg}")
                errors.append(error_msg)
            
            # Determine overall status
            if errors:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message=f"Crew validation failed with {len(errors)} errors",
                    details={'errors': errors, 'warnings': warnings},
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                )
            else:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.PASSED,
                    message="Crew validation passed",
                    details={'warnings': warnings, 'available_agents': len(available_agents) if available_agents else 0},
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                )
                
        except Exception as e:
            error_msg = f"Crew validation check failed: {str(e)}"
            logger.error(f"[CrewValidation] ❌ {error_msg}")
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.FAILED,
                message=error_msg,
                details={'traceback': traceback.format_exc()},
                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
            )


class StartupValidator:
    """Main startup validator that orchestrates all health checks."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.checks: List[HealthCheck] = []
        self._load_default_checks()
    
    def _load_default_checks(self) -> None:
        """Load default health checks."""
        self.checks = [
            ConfigurationCheck(),
            LLMProviderCheck(),
            ToolConfigurationCheck(),
            DatabaseConnectivityCheck(),
            TeamMappingCheck(),
            AgentInitializationCheck(),
            CrewValidationCheck(),
        ]
    
    def add_check(self, check: HealthCheck) -> None:
        """Add a custom health check."""
        self.checks.append(check)
    
    def remove_check(self, check_name: str) -> None:
        """Remove a health check by name."""
        self.checks = [check for check in self.checks if check.name != check_name]
    
    async def validate(self, context: Optional[Dict[str, Any]] = None) -> ValidationReport:
        """Execute all health checks and generate a validation report."""
        if context is None:
            context = {}
        
        report = ValidationReport(overall_status=CheckStatus.PASSED)
        
        logger.info("🔍 Starting system health checks...")
        
        for check in self.checks:
            logger.info(f"🔍 Running check: {check}")
            
            try:
                result = await check.execute(context)
                report.add_check(result)
                
                if result.status == CheckStatus.FAILED:
                    logger.error(f"❌ Check failed: {check.name} - {result.message}")
                elif result.status == CheckStatus.WARNING:
                    logger.warning(f"⚠️ Check warning: {check.name} - {result.message}")
                else:
                    logger.info(f"✅ Check passed: {check.name}")
                    
            except Exception as e:
                logger.error(f"❌ Check execution failed: {check.name} - {str(e)}")
                error_result = CheckResult(
                    name=check.name,
                    category=check.category,
                    status=CheckStatus.FAILED,
                    message=f"Check execution failed: {str(e)}",
                    error=e
                )
                report.add_check(error_result)
        
        # Determine overall status
        critical_failures = [check for check in report.checks 
                           if check.status == CheckStatus.FAILED]
        
        if critical_failures:
            report.overall_status = CheckStatus.FAILED
            report.recommendations.append("Fix critical failures before starting the system")
        elif any(check.status == CheckStatus.WARNING for check in report.checks):
            report.overall_status = CheckStatus.WARNING
            report.recommendations.append("Review warnings and consider addressing them")
        
        # Generate additional recommendations
        self._generate_recommendations(report)
        
        logger.info(f"🔍 Health checks completed. Overall status: {report.overall_status.value}")
        
        return report
    
    def _generate_recommendations(self, report: ValidationReport) -> None:
        """Generate recommendations based on check results."""
        if not report.is_healthy():
            report.recommendations.extend([
                "Review error logs for detailed failure information",
                "Check environment variables and configuration files",
                "Verify external service connectivity",
                "Ensure all required dependencies are installed"
            ])
        
        # Category-specific recommendations
        for check in report.checks:
            if check.status == CheckStatus.FAILED:
                if check.category == CheckCategory.LLM:
                    report.recommendations.append("Verify LLM API key and provider configuration")
                elif check.category == CheckCategory.AGENT:
                    report.recommendations.append("Check agent configuration and initialization logic")
                elif check.category == CheckCategory.TOOL:
                    report.recommendations.append("Verify tool dependencies and configuration")
                elif check.category == CheckCategory.DATABASE:
                    report.recommendations.append("Check database credentials and connectivity")
    
    def print_report(self, report: ValidationReport) -> None:
        """Print a formatted validation report."""
        print("\n" + "="*80)
        print("🚀 SYSTEM HEALTH CHECK REPORT")
        print("="*80)
        
        print(f"\n📊 Overall Status: {report.overall_status.value}")
        
        # Summary by category
        print("\n📈 Summary by Category:")
        for category, status_counts in report.summary.items():
            print(f"  {category.value}:")
            for status, count in status_counts.items():
                if count > 0:
                    print(f"    {status.value}: {count}")
        
        # Critical failures
        if report.critical_failures:
            print(f"\n❌ Critical Failures ({len(report.critical_failures)}):")
            for failure in report.critical_failures:
                print(f"  • {failure}")
        
        # Warnings
        if report.warnings:
            print(f"\n⚠️ Warnings ({len(report.warnings)}):")
            for warning in report.warnings:
                print(f"  • {warning}")
        
        # Detailed results
        print(f"\n🔍 Detailed Results ({len(report.checks)} checks):")
        for check in report.checks:
            status_icon = {
                CheckStatus.PASSED: "✅",
                CheckStatus.FAILED: "❌",
                CheckStatus.WARNING: "⚠️",
                CheckStatus.SKIPPED: "⏭️"
            }.get(check.status, "❓")
            
            print(f"  {status_icon} {check.category.value}: {check.name}")
            print(f"      Status: {check.status.value}")
            print(f"      Message: {check.message}")
            if check.duration_ms:
                print(f"      Duration: {check.duration_ms:.2f}ms")
            if check.details:
                print(f"      Details: {check.details}")
            if check.error:
                print(f"      Error: {check.error}")
            print()
        
        # Recommendations
        if report.recommendations:
            print("💡 Recommendations:")
            for i, recommendation in enumerate(report.recommendations, 1):
                print(f"  {i}. {recommendation}")
        
        print("="*80)


async def run_startup_validation(team_id: str = "KAI") -> ValidationReport:
    """Convenience function to run startup validation."""
    validator = StartupValidator()
    context = {"team_id": team_id}
    
    report = await validator.validate(context)
    validator.print_report(report)
    
    return report


if __name__ == "__main__":
    # Run validation when executed directly
    asyncio.run(run_startup_validation()) 