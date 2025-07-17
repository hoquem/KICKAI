"""
KICKAI Tasks Package

This package contains unified task management functionality for the KICKAI system.
All task creation is now handled through the TaskRegistry system.
"""

from .tasks import Task, TaskStatus
from .task_templates import (
    TaskParameter,
    TaskParameterType,
    TaskTemplate,
    TaskRegistry,
    TASK_REGISTRY,
    TaskParameterValidationError,
    TaskParameterValidator
)

__all__ = [
    # Core task types
    'Task',
    'TaskStatus',
    
    # Template system
    'TaskParameter',
    'TaskParameterType',
    'TaskTemplate',
    'TaskParameterValidationError',
    'TaskParameterValidator',
    
    # Registry system
    'TaskRegistry',
    'TASK_REGISTRY'
] 