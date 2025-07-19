"""
Centralized ID Processing Service - Single Source of Truth

This module provides a centralized service for processing, validating, and normalizing
all types of IDs used in the KICKAI system (player IDs, team IDs, equipment IDs, etc.).

This follows the single source of truth principle - all ID processing logic should
go through this service to ensure consistency across the entire system.
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class IDType(Enum):
    """Types of IDs that can be processed."""
    PLAYER_ID = "player_id"
    TEAM_ID = "team_id"
    EQUIPMENT_ID = "equipment_id"
    MATCH_ID = "match_id"
    PAYMENT_ID = "payment_id"
    PHONE_NUMBER = "phone_number"
    EMAIL = "email"
    USERNAME = "username"


@dataclass
class ProcessedID:
    """Result of ID processing."""
    id_type: IDType
    original_value: str
    normalized_value: str
    is_valid: bool
    confidence: float  # 0.0 to 1.0
    validation_errors: List[str]
    extracted_from: str  # Source text where ID was found
    extraction_method: str  # Method used to extract the ID


@dataclass
class EntityExtractionResult:
    """Result of entity extraction from text."""
    entities: Dict[str, ProcessedID]
    extraction_method: str
    confidence: float
    source_text: str
    processing_time_ms: float


class IDProcessor:
    """
    Centralized ID processing service - the single source of truth for all ID operations.
    
    This service handles:
    - ID extraction from text
    - ID validation and normalization
    - ID format conversion
    - Entity extraction for commands
    """
    
    def __init__(self):
        # Define ID patterns and validation rules
        self.id_patterns = {
            IDType.PLAYER_ID: {
                'pattern': r'\b[a-zA-Z]{2,4}\d*\b',
                'validation_rules': [
                    lambda x: len(x) >= 2 and len(x) <= 6,
                    lambda x: x[0].isalpha(),
                    lambda x: x.isalnum()
                ],
                'normalization': lambda x: x.upper().strip()
            },
            IDType.TEAM_ID: {
                'pattern': r'\b[A-Z]{2,4}\b',
                'validation_rules': [
                    lambda x: len(x) >= 2 and len(x) <= 4,
                    lambda x: x.isalpha(),
                    lambda x: x.isupper()
                ],
                'normalization': lambda x: x.upper().strip()
            },
            IDType.PHONE_NUMBER: {
                'pattern': r'\b(?:\+?44|0)?[17]\d{9}\b',
                'validation_rules': [
                    lambda x: len(x) >= 10 and len(x) <= 13,
                    lambda x: re.match(r'^[\d\+]+$', x)
                ],
                'normalization': self._normalize_phone_number
            },
            IDType.EMAIL: {
                'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'validation_rules': [
                    lambda x: '@' in x,
                    lambda x: '.' in x.split('@')[1]
                ],
                'normalization': lambda x: x.lower().strip()
            },
            IDType.MATCH_ID: {
                'pattern': r'\bMATCH\d{3,6}\b',
                'validation_rules': [
                    lambda x: x.startswith('MATCH'),
                    lambda x: x[5:].isdigit()
                ],
                'normalization': lambda x: x.upper().strip()
            }
        }
        
        # NOTE: Command definitions have been removed from this file to maintain
        # single source of truth. Commands should be defined in their respective
        # feature modules under src/features/*/application/commands/
        
        logger.info("IDProcessor initialized with ID patterns and validation rules")
    
    def _normalize_phone_number(self, phone: str) -> str:
        """Normalize phone number to standard format."""
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d\+]', '', phone)
        
        # Handle UK numbers
        if cleaned.startswith('0'):
            cleaned = '+44' + cleaned[1:]
        elif cleaned.startswith('44'):
            cleaned = '+' + cleaned
        elif not cleaned.startswith('+'):
            cleaned = '+44' + cleaned
            
        return cleaned
    
    def extract_entities_from_text(self, text: str, expected_entities: Optional[List[IDType]] = None) -> EntityExtractionResult:
        """
        Extract entities from text using pattern matching.
        
        Args:
            text: Text to extract entities from
            expected_entities: List of expected entity types (if None, extract all)
            
        Returns:
            EntityExtractionResult containing extracted entities
        """
        start_time = datetime.now()
        entities = {}
        
        # Determine which entity types to extract
        entity_types = expected_entities if expected_entities else list(IDType)
        
        for entity_type in entity_types:
            if entity_type not in self.id_patterns:
                continue
                
            pattern = self.id_patterns[entity_type]['pattern']
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                value = match.group()
                processed_id = self._process_id(value, entity_type, text)
                
                if processed_id.is_valid:
                    entities[entity_type.value] = processed_id
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return EntityExtractionResult(
            entities=entities,
            extraction_method="pattern_matching",
            confidence=0.8 if entities else 0.0,
            source_text=text,
            processing_time_ms=processing_time
        )
    
    def extract_entities_from_command(self, command_text: str, command_name: str) -> EntityExtractionResult:
        """
        Extract entities from a command text.
        
        Args:
            command_text: The command text (e.g., "/register AB1 07123456789")
            command_name: The command name (e.g., "register")
            
        Returns:
            EntityExtractionResult containing extracted entities
        """
        # Remove command prefix and split into parts
        parts = command_text.strip().split()
        if not parts:
            return EntityExtractionResult(
                entities={},
                extraction_method="command_parsing",
                confidence=0.0,
                source_text=command_text,
                processing_time_ms=0.0
            )
        
        # Extract entities from command parameters
        entities = {}
        for part in parts[1:]:  # Skip command name
            # Try to identify entity type based on pattern
            for entity_type, config in self.id_patterns.items():
                if re.match(config['pattern'], part, re.IGNORECASE):
                    processed_id = self._process_id(part, entity_type, command_text)
                    if processed_id.is_valid:
                        entities[entity_type.value] = processed_id
                        break
        
        return EntityExtractionResult(
            entities=entities,
            extraction_method="command_parsing",
            confidence=0.9 if entities else 0.0,
            source_text=command_text,
            processing_time_ms=0.0
        )
    
    def _process_id(self, value: str, id_type: IDType, source_text: str) -> ProcessedID:
        """
        Process a single ID value.
        
        Args:
            value: The ID value to process
            id_type: The type of ID
            source_text: The source text where the ID was found
            
        Returns:
            ProcessedID containing processing results
        """
        if id_type not in self.id_patterns:
            return ProcessedID(
                id_type=id_type,
                original_value=value,
                normalized_value=value,
                is_valid=False,
                confidence=0.0,
                validation_errors=["Unknown ID type"],
                extracted_from=source_text,
                extraction_method="unknown"
            )
        
        config = self.id_patterns[id_type]
        validation_errors = []
        
        # Apply validation rules
        for rule in config['validation_rules']:
            try:
                if not rule(value):
                    validation_errors.append(f"Failed validation rule: {rule.__name__ if hasattr(rule, '__name__') else 'unknown'}")
            except Exception as e:
                validation_errors.append(f"Validation error: {str(e)}")
        
        # Normalize the value
        try:
            normalized_value = config['normalization'](value)
        except Exception as e:
            normalized_value = value
            validation_errors.append(f"Normalization error: {str(e)}")
        
        is_valid = len(validation_errors) == 0
        confidence = 1.0 if is_valid else max(0.0, 1.0 - len(validation_errors) * 0.2)
        
        return ProcessedID(
            id_type=id_type,
            original_value=value,
            normalized_value=normalized_value,
            is_valid=is_valid,
            confidence=confidence,
            validation_errors=validation_errors,
            extracted_from=source_text,
            extraction_method="pattern_matching"
        )
    
    def validate_id(self, value: str, id_type: IDType) -> Tuple[bool, List[str]]:
        """
        Validate an ID value.
        
        Args:
            value: The ID value to validate
            id_type: The type of ID
            
        Returns:
            Tuple of (is_valid, validation_errors)
        """
        processed_id = self._process_id(value, id_type, "")
        return processed_id.is_valid, processed_id.validation_errors
    
    def normalize_id(self, value: str, id_type: IDType) -> str:
        """
        Normalize an ID value.
        
        Args:
            value: The ID value to normalize
            id_type: The type of ID
            
        Returns:
            Normalized ID value
        """
        processed_id = self._process_id(value, id_type, "")
        return processed_id.normalized_value
    
    def get_entity_value(self, entities: Dict[str, ProcessedID], entity_name: str) -> Optional[str]:
        """
        Get the normalized value of an entity.
        
        Args:
            entities: Dictionary of entities
            entity_name: Name of the entity to get
            
        Returns:
            Normalized entity value or None if not found
        """
        if entity_name in entities:
            return entities[entity_name].normalized_value
        return None


# Global instance
_id_processor: Optional[IDProcessor] = None

def get_id_processor() -> IDProcessor:
    """Get the global ID processor instance."""
    global _id_processor
    if _id_processor is None:
        _id_processor = IDProcessor()
    return _id_processor

# Convenience functions
def extract_entities_from_text(text: str, expected_entities: Optional[List[IDType]] = None) -> EntityExtractionResult:
    """Extract entities from text."""
    return get_id_processor().extract_entities_from_text(text, expected_entities)

def extract_entities_from_command(command_text: str, command_name: str) -> EntityExtractionResult:
    """Extract entities from command text."""
    return get_id_processor().extract_entities_from_command(command_text, command_name)

def validate_id(value: str, id_type: IDType) -> Tuple[bool, List[str]]:
    """Validate an ID value."""
    return get_id_processor().validate_id(value, id_type)

def normalize_id(value: str, id_type: IDType) -> str:
    """Normalize an ID value."""
    return get_id_processor().normalize_id(value, id_type) 