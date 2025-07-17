"""
Unified Task Registry and Template System for KICKAI.

This module provides a consolidated approach to task management through
templates and a unified registry system.
"""

import logging
from typing import Dict, Any, List, Optional, Type, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import uuid

from .tasks import Task, TaskStatus

logger = logging.getLogger(__name__)


class TaskParameterType(Enum):
    """Task parameter types."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


@dataclass
class TaskParameter:
    """Task parameter definition."""
    name: str
    type: Union[TaskParameterType, Type]
    description: str
    required: bool = True
    default: Optional[Any] = None


class TaskParameterValidationError(Exception):
    """Custom exception for task parameter validation errors."""
    def __init__(self, errors: List[str], template_id: Optional[str] = None):
        self.errors = errors
        self.template_id = template_id
        message = f"Parameter validation failed"
        if template_id:
            message += f" for template '{template_id}'"
        message += f": {errors}"
        super().__init__(message)


class TaskParameterValidator:
    """Centralized parameter validation logic for tasks."""
    @staticmethod
    def validate(parameters: Dict[str, Any], param_defs: List[TaskParameter]) -> List[str]:
        errors = []
        for param in param_defs:
            if param.required and param.name not in parameters:
                errors.append(f"Missing required parameter: {param.name}")
                continue
            if param.name in parameters:
                value = parameters[param.name]
                # Handle type validation
                if isinstance(param.type, TaskParameterType):
                    if param.type == TaskParameterType.STRING and not isinstance(value, str):
                        errors.append(f"Parameter '{param.name}' must be a string")
                    elif param.type == TaskParameterType.INTEGER and not isinstance(value, int):
                        errors.append(f"Parameter '{param.name}' must be an integer")
                    elif param.type == TaskParameterType.FLOAT and not isinstance(value, (int, float)):
                        errors.append(f"Parameter '{param.name}' must be a number")
                    elif param.type == TaskParameterType.BOOLEAN and not isinstance(value, bool):
                        errors.append(f"Parameter '{param.name}' must be a boolean")
                else:
                    if not isinstance(value, param.type):
                        errors.append(f"Parameter '{param.name}' must be of type {param.type.__name__}")
        return errors


@dataclass
class TaskTemplate:
    """Task template definition."""
    id: str
    name: str
    description: str
    parameters: List[TaskParameter]
    agent_type: str
    priority: int = 1
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> List[str]:
        return TaskParameterValidator.validate(parameters, self.parameters)
    
    def instantiate(self, parameters: Dict[str, Any], task_id: Optional[str] = None) -> Task:
        errors = self.validate_parameters(parameters)
        if errors:
            raise TaskParameterValidationError(errors, template_id=self.id)
        if task_id is None:
            task_id = f"{self.id}_{uuid.uuid4().hex[:8]}"
        return Task(
            id=task_id,
            name=self.name,
            description=self.description,
            status=TaskStatus.PENDING,
            parameters=parameters,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            template_name=self.id
        )


class TaskRegistry:
    """Unified registry for task templates and task creation."""
    
    def __init__(self):
        self.templates: Dict[str, TaskTemplate] = {}
        self._initialize_default_templates()
        logger.info("TaskRegistry initialized with default templates")
    
    def _initialize_default_templates(self):
        """Initialize default task templates."""
        # Message processing template
        message_processing = TaskTemplate(
            id="message_processing",
            name="Message Processing",
            description="Process user message",
            parameters=[
                TaskParameter("message", TaskParameterType.STRING, "User message", True),
                TaskParameter("user_id", TaskParameterType.STRING, "User ID", True)
            ],
            agent_type="message_processor",
            priority=2
        )
        self.register_template(message_processing)
        
        # Player registration template
        player_registration = TaskTemplate(
            id="player_registration",
            name="Player Registration",
            description="Register a new player",
            parameters=[
                TaskParameter("player", TaskParameterType.OBJECT, "Player information", True)
            ],
            agent_type="player_coordinator",
            priority=1
        )
        self.register_template(player_registration)
        
        # Payment processing template
        payment_processing = TaskTemplate(
            id="payment_processing",
            name="Payment Processing",
            description="Process payment",
            parameters=[
                TaskParameter("payment", TaskParameterType.OBJECT, "Payment information", True)
            ],
            agent_type="finance_manager",
            priority=1
        )
        self.register_template(payment_processing)
        
        # Team creation template
        team_creation = TaskTemplate(
            id="team_creation",
            name="Team Creation",
            description="Create a new team",
            parameters=[
                TaskParameter("team", TaskParameterType.OBJECT, "Team information", True)
            ],
            agent_type="team_manager",
            priority=1
        )
        self.register_template(team_creation)
        
        # Fixture creation template
        fixture_creation = TaskTemplate(
            id="fixture_creation",
            name="Fixture Creation",
            description="Create a new fixture",
            parameters=[
                TaskParameter("fixture", TaskParameterType.OBJECT, "Fixture information", True)
            ],
            agent_type="fixture_manager",
            priority=1
        )
        self.register_template(fixture_creation)
        
        # Bot configuration template
        bot_config = TaskTemplate(
            id="bot_configuration",
            name="Bot Configuration",
            description="Configure a bot instance",
            parameters=[
                TaskParameter("bot_data", TaskParameterType.OBJECT, "Bot configuration data", True)
            ],
            agent_type="bot_manager",
            priority=1
        )
        self.register_template(bot_config)
        
        # Command logging template
        command_logging = TaskTemplate(
            id="command_logging",
            name="Command Logging",
            description="Log a command execution",
            parameters=[
                TaskParameter("command_data", TaskParameterType.OBJECT, "Command execution data", True)
            ],
            agent_type="system_logger",
            priority=3
        )
        self.register_template(command_logging)
    
    def register_template(self, template: TaskTemplate) -> None:
        self.templates[template.id] = template
        logger.debug(f"Registered task template: {template.id}")
    
    def get_template(self, template_id: str) -> Optional[TaskTemplate]:
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[TaskTemplate]:
        return list(self.templates.values())
    
    def get_templates_by_agent_type(self, agent_type: str) -> List[TaskTemplate]:
        return [t for t in self.templates.values() if t.agent_type == agent_type]
    
    def create_task(self, template_id: str, parameters: Dict[str, Any], 
                   task_id: Optional[str] = None) -> Task:
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        try:
            return template.instantiate(parameters, task_id)
        except TaskParameterValidationError as e:
            logger.error(f"Task parameter validation error: {e}")
            raise
    
    def create_message_processing_task(self, message: str, user_id: str) -> Task:
        return self.create_task("message_processing", {
            "message": message,
            "user_id": user_id
        })
    
    def create_player_registration_task(self, player: Any) -> Task:
        return self.create_task("player_registration", {
            "player": player
        })
    
    def create_payment_processing_task(self, payment: Any) -> Task:
        return self.create_task("payment_processing", {
            "payment": payment
        })
    
    def create_team_creation_task(self, team: Any) -> Task:
        return self.create_task("team_creation", {
            "team": team
        })
    
    def create_fixture_creation_task(self, fixture: Any) -> Task:
        return self.create_task("fixture_creation", {
            "fixture": fixture
        })
    
    def create_bot_configuration_task(self, bot_data: Dict[str, Any]) -> Task:
        return self.create_task("bot_configuration", {
            "bot_data": bot_data
        })
    
    def create_command_logging_task(self, command_data: Dict[str, Any]) -> Task:
        return self.create_task("command_logging", {
            "command_data": command_data
        })


# Global task registry instance
TASK_REGISTRY = TaskRegistry() 