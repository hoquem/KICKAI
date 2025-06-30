#!/usr/bin/env python3
"""
Task Template System for Dynamic Task Decomposition

This module provides a template-based system for creating and managing tasks
that can be dynamically decomposed from complex user requests.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    """Task priority levels for execution ordering."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5

class TaskStatus(Enum):
    """Task status for tracking execution progress."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TaskParameter:
    """Represents a parameter required by a task template."""
    name: str
    description: str
    required: bool = True
    default_value: Any = None
    parameter_type: str = "string"  # string, number, boolean, list, dict
    validation_regex: Optional[str] = None
    allowed_values: Optional[List[Any]] = None
    
    def validate(self, value: Any) -> bool:
        """Validate a parameter value."""
        if self.required and value is None:
            return False
        
        if value is None and not self.required:
            return True
        
        # Type validation
        if self.parameter_type == "string" and not isinstance(value, str):
            return False
        elif self.parameter_type == "number" and not isinstance(value, (int, float)):
            return False
        elif self.parameter_type == "boolean" and not isinstance(value, bool):
            return False
        elif self.parameter_type == "list" and not isinstance(value, list):
            return False
        elif self.parameter_type == "dict" and not isinstance(value, dict):
            return False
        
        # Regex validation
        if self.validation_regex and isinstance(value, str):
            if not re.match(self.validation_regex, value):
                return False
        
        # Allowed values validation
        if self.allowed_values and value not in self.allowed_values:
            return False
        
        return True

@dataclass
class TaskTemplate:
    """Represents a task template that can be instantiated with parameters."""
    name: str
    description: str
    agent_type: str  # The type of agent that should execute this task
    parameters: List[TaskParameter] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.NORMAL
    estimated_duration: int = 30  # Estimated duration in seconds
    dependencies: List[str] = field(default_factory=list)  # Names of tasks this depends on
    tags: Set[str] = field(default_factory=set)  # Tags for categorization
    
    def validate_parameters(self, params: Dict[str, Any]) -> Dict[str, str]:
        """Validate parameters and return any errors."""
        errors = {}
        
        # Check for required parameters
        for param in self.parameters:
            if param.required and param.name not in params:
                errors[param.name] = f"Required parameter '{param.name}' is missing"
            elif param.name in params and not param.validate(params[param.name]):
                errors[param.name] = f"Parameter '{param.name}' has invalid value"
        
        # Check for unknown parameters
        valid_param_names = {param.name for param in self.parameters}
        for param_name in params:
            if param_name not in valid_param_names:
                errors[param_name] = f"Unknown parameter '{param_name}'"
        
        return errors
    
    def instantiate(self, params: Dict[str, Any], task_id: str) -> 'Task':
        """Create a Task instance from this template with the given parameters."""
        errors = self.validate_parameters(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        
        return Task(
            task_id=task_id,
            template_name=self.name,
            description=self.description,
            agent_type=self.agent_type,
            parameters=params,
            priority=self.priority,
            estimated_duration=self.estimated_duration,
            dependencies=self.dependencies.copy(),
            tags=self.tags.copy()
        )

@dataclass
class Task:
    """Represents an instantiated task ready for execution."""
    task_id: str
    template_name: str
    description: str
    agent_type: str
    parameters: Dict[str, Any]
    priority: TaskPriority
    estimated_duration: int
    dependencies: List[str]
    tags: Set[str]
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class TaskTemplateRegistry:
    """Registry for managing task templates."""
    
    def __init__(self):
        self.templates: Dict[str, TaskTemplate] = {}
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize default task templates for football team management."""
        
        # Player Management Templates
        self.register_template(TaskTemplate(
            name="add_player",
            description="Add a new player to the team roster",
            agent_type="player_coordinator",
            parameters=[
                TaskParameter("name", "Player's full name", required=True),
                TaskParameter("phone_number", "Player's phone number", required=True),
                TaskParameter("position", "Player's position", required=False, default_value="Unknown"),
                TaskParameter("jersey_number", "Player's jersey number", required=False, parameter_type="number"),
                TaskParameter("date_of_birth", "Player's date of birth", required=False),
                TaskParameter("emergency_contact", "Emergency contact information", required=False)
            ],
            priority=TaskPriority.HIGH,
            estimated_duration=45,
            tags={"player_management", "roster", "onboarding"}
        ))
        
        self.register_template(TaskTemplate(
            name="get_player_info",
            description="Retrieve information about a specific player",
            agent_type="player_coordinator",
            parameters=[
                TaskParameter("phone_number", "Player's phone number", required=True),
                TaskParameter("include_history", "Include player history", required=False, default_value=False, parameter_type="boolean")
            ],
            priority=TaskPriority.NORMAL,
            estimated_duration=15,
            tags={"player_management", "information", "lookup"}
        ))
        
        self.register_template(TaskTemplate(
            name="list_all_players",
            description="List all players in the team roster",
            agent_type="player_coordinator",
            parameters=[
                TaskParameter("include_inactive", "Include inactive players", required=False, default_value=False, parameter_type="boolean"),
                TaskParameter("sort_by", "Sort order", required=False, default_value="name", allowed_values=["name", "position", "jersey_number"])
            ],
            priority=TaskPriority.NORMAL,
            estimated_duration=20,
            tags={"player_management", "roster", "listing"}
        ))
        
        # Match Management Templates
        self.register_template(TaskTemplate(
            name="create_match",
            description="Create a new match fixture",
            agent_type="match_analyst",
            parameters=[
                TaskParameter("opponent", "Opposing team name", required=True),
                TaskParameter("match_date", "Match date (YYYY-MM-DD)", required=True, validation_regex=r"^\d{4}-\d{2}-\d{2}$"),
                TaskParameter("kickoff_time", "Kickoff time (HH:MM)", required=True, validation_regex=r"^\d{2}:\d{2}$"),
                TaskParameter("venue", "Match venue", required=True),
                TaskParameter("competition", "Competition type", required=False, default_value="League"),
                TaskParameter("notes", "Additional notes", required=False)
            ],
            priority=TaskPriority.HIGH,
            estimated_duration=60,
            tags={"match_management", "fixtures", "scheduling"}
        ))
        
        self.register_template(TaskTemplate(
            name="list_matches",
            description="List upcoming and past matches",
            agent_type="match_analyst",
            parameters=[
                TaskParameter("filter_type", "Filter type", required=False, default_value="upcoming", allowed_values=["upcoming", "past", "all"]),
                TaskParameter("limit", "Maximum number of matches to return", required=False, default_value=10, parameter_type="number")
            ],
            priority=TaskPriority.NORMAL,
            estimated_duration=25,
            tags={"match_management", "fixtures", "listing"}
        ))
        
        # Team Management Templates
        self.register_template(TaskTemplate(
            name="get_team_info",
            description="Get general team information",
            agent_type="team_manager",
            parameters=[
                TaskParameter("include_stats", "Include team statistics", required=False, default_value=False, parameter_type="boolean"),
                TaskParameter("include_finances", "Include financial information", required=False, default_value=False, parameter_type="boolean")
            ],
            priority=TaskPriority.NORMAL,
            estimated_duration=20,
            tags={"team_management", "information"}
        ))
        
        self.register_template(TaskTemplate(
            name="update_team_info",
            description="Update team information",
            agent_type="team_manager",
            parameters=[
                TaskParameter("field", "Field to update", required=True, allowed_values=["name", "description", "contact_info"]),
                TaskParameter("value", "New value", required=True)
            ],
            priority=TaskPriority.HIGH,
            estimated_duration=30,
            tags={"team_management", "update"}
        ))
        
        # Communication Templates
        self.register_template(TaskTemplate(
            name="send_team_message",
            description="Send a message to all team members",
            agent_type="communication_specialist",
            parameters=[
                TaskParameter("message", "Message content", required=True),
                TaskParameter("priority", "Message priority", required=False, default_value="normal", allowed_values=["urgent", "normal", "low"]),
                TaskParameter("include_leadership", "Include leadership group", required=False, default_value=False, parameter_type="boolean")
            ],
            priority=TaskPriority.NORMAL,
            estimated_duration=30,
            tags={"communication", "messaging", "broadcast"}
        ))
        
        self.register_template(TaskTemplate(
            name="create_availability_poll",
            description="Create an availability poll for a match",
            agent_type="communication_specialist",
            parameters=[
                TaskParameter("match_id", "Match identifier", required=True),
                TaskParameter("poll_question", "Poll question", required=False, default_value="Are you available for this match?"),
                TaskParameter("options", "Poll options", required=False, default_value=["Available", "Not Available", "Maybe"], parameter_type="list")
            ],
            priority=TaskPriority.HIGH,
            estimated_duration=45,
            tags={"communication", "polling", "availability"}
        ))
        
        # Financial Management Templates
        self.register_template(TaskTemplate(
            name="track_payment",
            description="Track a payment for a player",
            agent_type="finance_manager",
            parameters=[
                TaskParameter("player_phone", "Player's phone number", required=True),
                TaskParameter("amount", "Payment amount", required=True, parameter_type="number"),
                TaskParameter("match_id", "Associated match", required=False),
                TaskParameter("payment_type", "Type of payment", required=False, default_value="match_fee", allowed_values=["match_fee", "subscription", "other"])
            ],
            priority=TaskPriority.HIGH,
            estimated_duration=30,
            tags={"finance", "payment", "tracking"}
        ))
        
        self.register_template(TaskTemplate(
            name="generate_payment_report",
            description="Generate a payment report",
            agent_type="finance_manager",
            parameters=[
                TaskParameter("start_date", "Report start date", required=False),
                TaskParameter("end_date", "Report end date", required=False),
                TaskParameter("player_phone", "Specific player", required=False),
                TaskParameter("include_pending", "Include pending payments", required=False, default_value=True, parameter_type="boolean")
            ],
            priority=TaskPriority.NORMAL,
            estimated_duration=60,
            tags={"finance", "reporting", "analysis"}
        ))
        
        # Squad Selection Templates
        self.register_template(TaskTemplate(
            name="select_squad",
            description="Select squad for a match",
            agent_type="squad_selection_specialist",
            parameters=[
                TaskParameter("match_id", "Match identifier", required=True),
                TaskParameter("squad_size", "Number of players to select", required=False, default_value=16, parameter_type="number"),
                TaskParameter("consider_availability", "Consider availability", required=False, default_value=True, parameter_type="boolean"),
                TaskParameter("consider_form", "Consider recent form", required=False, default_value=True, parameter_type="boolean")
            ],
            priority=TaskPriority.HIGH,
            estimated_duration=120,
            dependencies=["get_availability_data"],
            tags={"squad_selection", "tactical", "planning"}
        ))
        
        self.register_template(TaskTemplate(
            name="get_availability_data",
            description="Get player availability data for squad selection",
            agent_type="squad_selection_specialist",
            parameters=[
                TaskParameter("match_id", "Match identifier", required=True),
                TaskParameter("include_history", "Include historical availability", required=False, default_value=False, parameter_type="boolean")
            ],
            priority=TaskPriority.NORMAL,
            estimated_duration=45,
            tags={"squad_selection", "availability", "data"}
        ))
        
        # Analytics Templates
        self.register_template(TaskTemplate(
            name="analyze_team_performance",
            description="Analyze team performance and generate insights",
            agent_type="analytics_specialist",
            parameters=[
                TaskParameter("time_period", "Analysis period", required=False, default_value="last_month", allowed_values=["last_week", "last_month", "last_quarter", "season"]),
                TaskParameter("include_comparison", "Include comparison with previous period", required=False, default_value=True, parameter_type="boolean"),
                TaskParameter("focus_areas", "Specific areas to focus on", required=False, parameter_type="list")
            ],
            priority=TaskPriority.NORMAL,
            estimated_duration=180,
            tags={"analytics", "performance", "insights"}
        ))
        
        self.register_template(TaskTemplate(
            name="generate_match_report",
            description="Generate a detailed match report",
            agent_type="analytics_specialist",
            parameters=[
                TaskParameter("match_id", "Match identifier", required=True),
                TaskParameter("include_statistics", "Include detailed statistics", required=False, default_value=True, parameter_type="boolean"),
                TaskParameter("include_highlights", "Include match highlights", required=False, default_value=True, parameter_type="boolean"),
                TaskParameter("include_recommendations", "Include recommendations", required=False, default_value=True, parameter_type="boolean")
            ],
            priority=TaskPriority.NORMAL,
            estimated_duration=90,
            tags={"analytics", "reporting", "match_analysis"}
        ))
        
        logger.info(f"Initialized {len(self.templates)} default task templates")
    
    def register_template(self, template: TaskTemplate):
        """Register a new task template."""
        if template.name in self.templates:
            logger.warning(f"Overwriting existing template: {template.name}")
        
        self.templates[template.name] = template
        logger.info(f"Registered template: {template.name} ({template.agent_type})")
    
    def get_template(self, name: str) -> Optional[TaskTemplate]:
        """Get a template by name."""
        return self.templates.get(name)
    
    def list_templates(self, agent_type: Optional[str] = None, tags: Optional[Set[str]] = None) -> List[TaskTemplate]:
        """List templates, optionally filtered by agent type or tags."""
        templates = list(self.templates.values())
        
        if agent_type:
            templates = [t for t in templates if t.agent_type == agent_type]
        
        if tags:
            templates = [t for t in templates if tags.intersection(t.tags)]
        
        return templates
    
    def search_templates(self, query: str) -> List[TaskTemplate]:
        """Search templates by name, description, or tags."""
        query_lower = query.lower()
        results = []
        
        for template in self.templates.values():
            if (query_lower in template.name.lower() or
                query_lower in template.description.lower() or
                any(query_lower in tag.lower() for tag in template.tags)):
                results.append(template)
        
        return results
    
    def validate_template(self, template: TaskTemplate) -> List[str]:
        """Validate a template and return any errors."""
        errors = []
        
        # Check for required fields
        if not template.name:
            errors.append("Template name is required")
        if not template.description:
            errors.append("Template description is required")
        if not template.agent_type:
            errors.append("Agent type is required")
        
        # Check for valid agent type
        valid_agent_types = {
            "message_processing_specialist", "team_manager", "player_coordinator",
            "match_analyst", "communication_specialist", "finance_manager",
            "squad_selection_specialist", "analytics_specialist"
        }
        if template.agent_type not in valid_agent_types:
            errors.append(f"Invalid agent type: {template.agent_type}")
        
        # Check parameter names are unique
        param_names = [p.name for p in template.parameters]
        if len(param_names) != len(set(param_names)):
            errors.append("Parameter names must be unique")
        
        # Check dependencies exist
        for dep in template.dependencies:
            if dep not in self.templates:
                errors.append(f"Dependency template not found: {dep}")
        
        return errors

# Global registry instance
task_template_registry = TaskTemplateRegistry()

def get_task_template_registry() -> TaskTemplateRegistry:
    """Get the global task template registry."""
    return task_template_registry

def register_task_template(template: TaskTemplate):
    """Register a task template in the global registry."""
    task_template_registry.register_template(template)

def get_task_template(name: str) -> Optional[TaskTemplate]:
    """Get a task template by name from the global registry."""
    return task_template_registry.get_template(name)

def list_task_templates(agent_type: Optional[str] = None, tags: Optional[Set[str]] = None) -> List[TaskTemplate]:
    """List task templates from the global registry."""
    return task_template_registry.list_templates(agent_type, tags)

def search_task_templates(query: str) -> List[TaskTemplate]:
    """Search task templates from the global registry."""
    return task_template_registry.search_templates(query)
