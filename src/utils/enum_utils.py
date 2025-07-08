"""
Enum utilities for Firestore serialization.

This module provides utilities to convert enum objects to their string values
for proper serialization when saving to Firestore.
"""

from enum import Enum
from typing import Any, Dict


def serialize_enums_for_firestore(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert enum values to their string representations for Firestore serialization.
    
    Args:
        data: Dictionary containing data that may include enum values
        
    Returns:
        Dictionary with enum values converted to strings
    """
    serialized_data = {}
    
    for key, value in data.items():
        if isinstance(value, Enum):
            serialized_data[key] = value.value
        elif isinstance(value, dict):
            serialized_data[key] = serialize_enums_for_firestore(value)
        elif isinstance(value, list):
            serialized_data[key] = [
                serialize_enums_for_firestore(item) if isinstance(item, dict)
                else item.value if isinstance(item, Enum)
                else item
                for item in value
            ]
        else:
            serialized_data[key] = value
    
    return serialized_data


def serialize_enum_value(value: Any) -> Any:
    """
    Serialize a single value, converting enums to their string values.
    
    Args:
        value: Value that may be an enum
        
    Returns:
        Serialized value (enum converted to string, other values unchanged)
    """
    if isinstance(value, Enum):
        return value.value
    return value 