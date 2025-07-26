"""
Registry validation utilities.

This module provides validation for registry items and configurations.
"""

from typing import List, Optional
from dataclasses import dataclass
from loguru import logger

@dataclass
class ValidationError:
    """Represents a validation error."""
    field: str
    message: str
    severity: str = "error"

class RegistryValidator:
    """Validates registry items and configurations."""
    
    @staticmethod
    def validate_tool_registration(tool_metadata: dict) -> List[ValidationError]:
        """Validate tool registration metadata."""
        errors = []
        
        if not tool_metadata.get('name'):
            errors.append(ValidationError("name", "Tool name is required"))
        
        if not tool_metadata.get('description'):
            errors.append(ValidationError("description", "Tool description is required"))
        
        version = tool_metadata.get('version', '')
        if version and not RegistryValidator._is_valid_version(version):
            errors.append(ValidationError("version", "Version must be in format X.Y.Z"))
        
        return errors
    
    @staticmethod
    def validate_command_registration(command_metadata: dict) -> List[ValidationError]:
        """Validate command registration metadata."""
        errors = []
        
        name = command_metadata.get('name', '')
        if not name.startswith('/'):
            errors.append(ValidationError("name", "Command name must start with /"))
        
        if not command_metadata.get('handler'):
            errors.append(ValidationError("handler", "Command handler is required"))
        
        return errors
    
    @staticmethod
    def validate_service_registration(service_reg: dict) -> List[ValidationError]:
        """Validate service registration."""
        errors = []
        
        if not service_reg.get('interface'):
            errors.append(ValidationError("interface", "Service interface is required"))
        
        if not service_reg.get('implementation') and not service_reg.get('factory'):
            errors.append(ValidationError("implementation", "Service implementation or factory is required"))
        
        return errors
    
    @staticmethod
    def _is_valid_version(version: str) -> bool:
        """Check if version string is valid."""
        if not version:
            return True
        
        parts = version.split('.')
        if len(parts) != 3:
            return False
        
        try:
            for part in parts:
                int(part)
            return True
        except ValueError:
            return False 