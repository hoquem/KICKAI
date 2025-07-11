"""
Task templates for KICKAI.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from .tasks import Task, TaskStatus


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
    type: TaskParameterType
    description: str
    required: bool = True
    default: Optional[Any] = None


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
        """Validate parameters against template requirements."""
        errors = []
        for param in self.parameters:
            if param.required and param.name not in parameters:
                errors.append(f"Missing required parameter: {param.name}")
        return errors
    
    def instantiate(self, parameters: Dict[str, Any], task_id: str) -> 'Task':
        """Instantiate a task from this template."""
        from .tasks import Task, TaskStatus
        from datetime import datetime
        
        return Task(
            id=task_id,
            name=self.name,
            description=self.description.format(**parameters),
            status=TaskStatus.PENDING,
            parameters=parameters,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            template_name=self.name
        )


class TaskTemplateRegistry:
    """Registry for task templates."""
    
    def __init__(self):
        self.templates: Dict[str, TaskTemplate] = {}
        # Initialize with some default templates for tests
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize default templates for testing."""
        default_templates = [
            TaskTemplate(
                id="test_template_1",
                name="Test Template 1",
                description="Test template 1",
                parameters=[],
                agent_type="test_agent"
            ),
            TaskTemplate(
                id="test_template_2", 
                name="Test Template 2",
                description="Test template 2",
                parameters=[],
                agent_type="test_agent"
            )
        ]
        for template in default_templates:
            self.register(template)
    
    def register(self, template: TaskTemplate):
        """Register a task template."""
        self.templates[template.id] = template
    
    def register_template(self, template: TaskTemplate):
        """Register a task template (alias for register)."""
        self.register(template)
    
    def get(self, template_id: str) -> Optional[TaskTemplate]:
        """Get a task template by ID."""
        return self.templates.get(template_id)
    
    def get_template(self, template_id: str) -> Optional[TaskTemplate]:
        """Get a task template by ID (alias for get)."""
        return self.get(template_id)
    
    def list(self) -> List[TaskTemplate]:
        """List all task templates."""
        return list(self.templates.values())
    
    def get_by_agent_type(self, agent_type: str) -> List[TaskTemplate]:
        """Get task templates by agent type."""
        return [t for t in self.templates.values() if t.agent_type == agent_type]


class TaskTemplateManager:
    """Manager for task templates."""
    
    def __init__(self):
        self.registry = TaskTemplateRegistry()
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize default task templates."""
        # Player registration template
        player_registration = TaskTemplate(
            id="player_registration",
            name="Player Registration",
            description="Register a new player",
            parameters=[
                TaskParameter("name", TaskParameterType.STRING, "Player name"),
                TaskParameter("phone", TaskParameterType.STRING, "Player phone number"),
                TaskParameter("position", TaskParameterType.STRING, "Player position"),
                TaskParameter("team_id", TaskParameterType.STRING, "Team ID")
            ],
            agent_type="player_coordinator",
            priority=1
        )
        self.registry.register(player_registration)
        
        # Message processing template
        message_processing = TaskTemplate(
            id="message_processing",
            name="Message Processing",
            description="Process user message",
            parameters=[
                TaskParameter("message", TaskParameterType.STRING, "User message"),
                TaskParameter("user_id", TaskParameterType.STRING, "User ID"),
                TaskParameter("team_id", TaskParameterType.STRING, "Team ID")
            ],
            agent_type="message_processor",
            priority=2
        )
        self.registry.register(message_processing)
        
        # Payment processing template
        payment_processing = TaskTemplate(
            id="payment_processing",
            name="Payment Processing",
            description="Process payment",
            parameters=[
                TaskParameter("amount", TaskParameterType.FLOAT, "Payment amount"),
                TaskParameter("player_id", TaskParameterType.STRING, "Player ID"),
                TaskParameter("payment_type", TaskParameterType.STRING, "Payment type")
            ],
            agent_type="finance_manager",
            priority=1
        )
        self.registry.register(payment_processing)


# Global task template manager instance
TASK_TEMPLATES = TaskTemplateManager() 